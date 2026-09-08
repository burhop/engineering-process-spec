"""Run inside the network-disabled consumer container, using installed APIs only."""
from __future__ import annotations
from copy import deepcopy
import datetime
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path("/consumer")
records = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(path):
    return {p.relative_to(path).as_posix(): digest(p) for p in sorted(path.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def execute(label, command, expected=0):
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    (ROOT / (label + ".stdout")).write_text(result.stdout)
    (ROOT / (label + ".stderr")).write_text(result.stderr)
    records.append({"id": label, "argv": command, "expectedExit": expected, "actualExit": result.returncode})
    if result.returncode != expected:
        raise AssertionError(f"{label}: expected {expected}, observed {result.returncode}\n{result.stdout}\n{result.stderr}")
    return json.loads(result.stdout) if result.stdout.strip().startswith("{") else result.stdout


def assert_run(report, application):
    assert report["execution"]["status"] == "succeeded", report
    assert report["acceptance"]["status"] == "pass", report
    assert report["approval"] == "not-requested"
    assert len(report["calls"]) == 2
    assert {c["node"] for c in report["calls"]} == {"main/volume", "main/mass"}
    assert all(c["observedProvider"]["application"] == application for c in report["calls"])


def engineering_call_count():
    audit = ROOT / "provider-audit.jsonl"
    if not audit.exists():
        return 0
    return sum(json.loads(line).get("method") == "tools/call" for line in audit.read_text().splitlines())


def main():
    prepared = json.loads((ROOT / "prepared.json").read_text())
    execute("install-wheel", [sys.executable, "-m", "pip", "install", "--no-index", "--no-deps", str(ROOT / prepared["wheelFilename"])])
    import epx
    from epx.package import open_root, load
    before = tree(ROOT / "package")
    with open_root(ROOT / "package") as directory:
        assert load(directory).summary()["engineeringCalls"] == 0
    assert execute("python-validate", ["epx", "validate", "package"])["status"] == "valid"
    assert execute("python-inspect", ["epx", "inspect", "package"])["engineeringCalls"] == 0
    execute("python-preserve", ["epx", "preserve", "package", "saved-python"])
    assert tree(ROOT / "saved-python") == before
    execute("create-local-bindings", ["epx", "demo-bindings", "--provider", "/consumer/mock_mcp_server.py", "--out", "/consumer/local-bindings.json"])
    bindings = json.loads((ROOT / "local-bindings.json").read_text())
    bindings["bindings"]["engineering"]["transport"]["arguments"] += ["--audit", "/consumer/provider-audit.jsonl"]
    (ROOT / "local-bindings.json").write_text(json.dumps(bindings))
    assert execute("python-preflight", ["epx", "preflight", "package", "--bindings", "local-bindings.json"])["engineeringCalls"] == 0
    events = [json.loads(line) for line in (ROOT / "provider-audit.jsonl").read_text().splitlines()]
    assert not any(event.get("method") == "tools/call" for event in events)
    default_application = "urn:engineering-process-spec:mock-engineering"
    assert_run(execute("python-run", ["epx", "run", "package", "--bindings", "local-bindings.json", "--engine", "cwltool", "--out", "run-python"]), default_application)
    node_cli = ["node", "/consumer/node-consumer/node_modules/epx-node-adopter/cli.mjs"]
    assert execute("node-validate", node_cli + ["validate", "package"])["valid"] is True
    assert execute("node-inspect", node_cli + ["inspect", "package"])["engineeringCalls"] == 0
    execute("node-preserve", node_cli + ["preserve", "package", "--out", "saved-node"])
    assert tree(ROOT / "saved-node") == before
    before_preflight = engineering_call_count()
    assert execute("node-preflight", node_cli + ["preflight", "package", "--bindings", "local-bindings.json"])["engineeringCalls"] == 0
    assert engineering_call_count() == before_preflight
    assert_run(execute("node-run", node_cli + ["run", "package", "--bindings", "local-bindings.json", "--engine", "streamflow", "--out", "run-node"]), default_application)
    execute("node-public-api", ["node", "/consumer/node-consumer/integration.mjs"])
    (ROOT / "missing-bindings.json").write_text(json.dumps({"format": "epx-bindings", "version": "0.1.0-draft.1", "bindings": {}}))
    for label, prefix, code in (("python", ["epx"], 2), ("node", node_cli, 1)):
        before_preflight = engineering_call_count()
        missing = execute(label + "-unavailable", prefix + ["preflight", "package", "--bindings", "missing-bindings.json"], code)
        assert missing["status"] == "unavailable" and missing["engineeringCalls"] == 0
        assert engineering_call_count() == before_preflight
    requirements = json.loads((ROOT / "package/requirements.json").read_text())
    replacement = deepcopy(requirements["bindings"]["engineering"])
    replacement_application = "urn:engineering-process-spec:mock-other-engineering"
    replacement["application"]["id"] = replacement_application
    (ROOT / "intended-binding.json").write_text(json.dumps(replacement))
    replacement_bindings = deepcopy(bindings)
    replacement_bindings["bindings"]["engineering"]["application"]["id"] = replacement_application
    replacement_bindings["bindings"]["engineering"]["transport"]["arguments"] += ["--application", replacement_application]
    (ROOT / "replacement-bindings.json").write_text(json.dumps(replacement_bindings))
    for label, prefix, engine, code in (("python", ["epx"], "cwltool", 2), ("node", node_cli, "streamflow", 1)):
        new_package = "replaced-" + label
        execute(label + "-replace", prefix + ["replace", "package", "--binding", "engineering", "--with", "intended-binding.json", "--revision", "2", "--out", new_package])
        changed = json.loads((ROOT / new_package / "requirements.json").read_text())
        assert changed["process"]["id"] == requirements["process"]["id"] and changed["process"]["revision"] == "2"
        assert (ROOT / new_package / "workflow.cwl.json").read_bytes() == (ROOT / "package/workflow.cwl.json").read_bytes()
        before_preflight = engineering_call_count()
        execute(label + "-replacement-old-binding", prefix + ["preflight", new_package, "--bindings", "local-bindings.json"], code)
        execute(label + "-original-new-binding", prefix + ["preflight", "package", "--bindings", "replacement-bindings.json"], code)
        assert engineering_call_count() == before_preflight
        assert_run(execute(label + "-replacement-run", prefix + ["run", new_package, "--bindings", "replacement-bindings.json", "--engine", engine, "--out", "run-replaced-" + label]), replacement_application)
    assert tree(ROOT / "package") == before
    installed_sources = {
        "python": tree(Path(epx.__file__).parent),
        "node": tree(ROOT / "node-consumer/node_modules/epx-node-adopter"),
    }
    (ROOT / "installed-source-files.json").write_text(json.dumps(installed_sources, indent=2) + "\n")
    source_epochs = {key: {"files": len(value), "treeSha256": hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()} for key, value in installed_sources.items()}
    no_wright = all(importlib.util.find_spec(name) is None for name in ("wright", "workspace_service", "tool_registry"))
    assert no_wright
    evidence = {
        "format": "epx-adopter-walkthrough", "observedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "passed", "scope": "Installed artifacts and copied public calculation/provider only; no source repository/Wright mount; execution networking disabled",
        "artifacts": prepared, "sourceEpochs": source_epochs,
        "versions": {name: importlib.metadata.version(name) for name in ("engineering-process-kit", "cwltool", "streamflow", "jsonschema")},
        "python": sys.version.split()[0], "node": subprocess.check_output(["node", "--version"], text=True).strip(),
        "noWrightPackages": no_wright, "sourceBytesPreserved": True,
        "runReportSha256": {name: digest(ROOT / name / "report.json") for name in ("run-python", "run-node", "run-node-api", "run-replaced-python", "run-replaced-node")},
        "commands": records,
        "outcomes": {"python-cwltool": "2 actual MCP calls; execution succeeded; acceptance pass", "node-streamflow": "2 actual MCP calls; execution succeeded; acceptance pass", "publicNodeApi": "installed import + read/preflight/run passed", "replacement": "Both CLIs produced revision 2, rejected cross-bindings and executed explicitly configured replacement with new acceptance", "preflightEngineeringCalls": 0},
        "limits": ["Mock provider only; no real Solid Edge test", "No organizational adoption claim", "This walkthrough complements rather than replaces the full conformance suite", "npm dependency installation occurs before network-disabled execution"],
    }
    (ROOT / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
