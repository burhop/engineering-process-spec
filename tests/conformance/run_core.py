"""Black-box core conformance: invoke the public CLIs, never import their resolvers."""

from __future__ import annotations

import argparse
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
from queue import Empty, Queue
import re
import shutil
import subprocess
import sys
import tempfile
import tarfile
from threading import Thread
import time
import traceback
import uuid
import zipfile

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "conformance" / "cases.json"
PROVIDER = ROOT / "tests" / "providers" / "mock_mcp_server.py"
NODE_CLI = Path(os.environ.get("EPX_NODE_CLI", ROOT / "applications" / "node" / "cli.mjs")).resolve()
VERSION = "0.1.0-draft.1"
PROFILE = f"urn:engineering-process-spec:core:{VERSION}"
NEW_APPLICATION = "urn:engineering-process-spec:mock-other-engineering"
SUPPORTED_ROLES = ["reader", "editor", "binder", "executor", "adapter"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def is_valid(value: dict) -> bool:
    return value.get("valid") is True or value.get("status") == "valid"


def is_available(value: dict) -> bool:
    return value.get("status") in ("available", "ready")


def tree_digests(root: Path) -> dict:
    return {path.relative_to(root).as_posix(): digest(path) for path in sorted(root.rglob("*")) if path.is_file()}


def source_snapshot() -> dict:
    paths = [ROOT / "spec" / "core-draft.md", ROOT / "conformance" / "cases.json", Path(__file__).resolve(), PROVIDER]
    for pattern in ("src/epx/*.py", "applications/node/*.mjs", "applications/node/package*.json", "schemas/*.json", "examples/**/*.json", "tests/conformance/*.py"):
        paths.extend(ROOT.glob(pattern))
    return {path.relative_to(ROOT).as_posix(): digest(path) for path in sorted(set(paths)) if path.is_file()}


def reinventory(root: Path) -> None:
    """Hash deliberately edited fixture bytes; not an implementation-side repair."""
    metadata = read_json(root / "ro-crate-metadata.json")
    for entity in metadata["@graph"]:
        if entity.get("@type") == "File" and entity.get("@id") != "ro-crate-metadata.json":
            payload = root / entity["@id"]
            if payload.is_file():
                entity["sha256"] = digest(payload)
                entity["contentSize"] = str(payload.stat().st_size)
    write_json(root / "ro-crate-metadata.json", metadata)


class CheckFailed(AssertionError):
    pass


class CaseContext:
    def __init__(self, spec: dict, implementation: str, root: Path, timeout: int):
        self.spec, self.implementation, self.root, self.timeout = spec, implementation, root, timeout
        root.mkdir(parents=True)
        self.package = root / "package"
        self.package_source = ROOT / "examples" / spec["fixture"]
        shutil.copytree(self.package_source, self.package)
        self.audit = root / "provider-audit.jsonl"
        self.bindings_file = root / "bindings.json"
        self.run_directory = root / "run"
        self.checks, self.invocations = [], []
        self.original_source = tree_digests(self.package_source)
        self.initial_package = tree_digests(self.package)
        self.prepared_package = None
        self.configure()

    def check(self, name: str, actual, expected=True) -> None:
        passed = actual == expected
        self.checks.append({"assertion": name, "expected": expected, "observed": actual, "passed": passed})
        if not passed:
            raise CheckFailed(f"{name}: expected {expected!r}; observed {actual!r}")

    def configure(self) -> None:
        if self.spec.get("edit"):
            self.edit(self.spec["edit"])
        req = read_json(self.package / "requirements.json")
        intended = req["bindings"]["engineering"]
        arguments = [str(PROVIDER), "--audit", str(self.audit)]
        for field, flag in (("fault", "--fault"), ("faultTool", "--fault-tool"), ("resourceState", "--resource-state")):
            if self.spec.get(field):
                arguments += [flag, self.spec[field]]
        binding = {
            "implementation": {key: intended["implementation"][key] for key in ("id", "revision")},
            "application": deepcopy(intended["application"]),
            "transport": {"kind": "stdio", "command": sys.executable, "arguments": arguments},
            "trust": {"kind": "launcher-sha256", "path": str(PROVIDER), "sha256": digest(PROVIDER)},
        }
        if self.spec.get("edit") == "unverifiable-resource":
            shim = ROOT / "tests" / "conformance" / "resource_revision_shim.py"
            binding["transport"]["arguments"][0] = str(shim)
            binding["trust"].update(path=str(shim), sha256=digest(shim))
        self.bindings = {"format": "epx-bindings", "version": VERSION, "bindings": {"engineering": binding}}
        if self.spec.get("bindingEdit") == "other-binding":
            self.bindings["bindings"] = {"another-server": binding}
        elif self.spec.get("bindingEdit") == "launcher-digest":
            binding["trust"]["sha256"] = "0" * 64
        write_json(self.bindings_file, self.bindings)
        self.prepared_package = tree_digests(self.package)
        write_json(self.root / "fixture-provenance.json", {"source": str(self.package_source), "sourceDigests": self.original_source, "preparedDigests": self.prepared_package, "deliberateEdits": {key: self.spec[key] for key in ("edit", "bindingEdit", "fault", "faultTool", "resourceState") if key in self.spec}})

    def edit(self, mode: str) -> None:
        requirement_file = self.package / "requirements.json"
        workflow_file = self.package / "workflow.cwl.json"
        job_file = self.package / "inputs" / "job.json"
        req, workflow, job = read_json(requirement_file), read_json(workflow_file), read_json(job_file)
        main = next(entry for entry in workflow["$graph"] if entry["id"] == "#main")
        changed = None
        if mode == "unknown-feature":
            req["requiredFeatures"].append("required-human-approval"); changed = "requirements"
        elif mode in ("missing-crate-date", "missing-crate-license"):
            crate_path = self.package / "ro-crate-metadata.json"
            crate = read_json(crate_path)
            root = next(entity for entity in crate["@graph"] if entity.get("@id") == "./")
            root.pop("datePublished" if mode == "missing-crate-date" else "license", None)
            write_json(crate_path, crate)
        elif mode == "profile-version":
            req["version"] = "99.0.0-unsupported"; req["profile"] = "urn:engineering-process-spec:core:99.0.0-unsupported"; changed = "requirements"
        elif mode == "authority-mismatch":
            req["process"]["entrypoint"] = "other.cwl.json#main"; changed = "requirements"
        elif mode == "broken-reference":
            main["steps"]["mass"]["in"]["arguments_json"]["source"][0] = "nonexistent/result"; changed = "workflow"
        elif mode == "cycle":
            main["steps"]["volume"]["in"]["arguments_json"]["source"][0] = "mass/result"; changed = "workflow"
        elif mode == "operation-mismatch":
            main["steps"]["mass"]["in"]["binding"]["default"] = "different-binding"; changed = "workflow"
        elif mode == "missing-exchange":
            del main["requirements"]["epx:ExchangeRequirement"]; changed = "workflow"
        elif mode == "unknown-cwl":
            main["requirements"]["urn:engineering-process-spec:unsupported:CWLRequirement"] = {}; changed = "workflow"
        elif mode == "unknown-cwl-field":
            main["notAStandardCwlField"] = True; changed = "workflow"
        elif mode == "injected-context":
            job["epx_context"] = {"class": "File", "path": "receiving-secret-context.json"}; changed = "job"
        elif mode == "missing-job-record-field":
            job["length"].pop("quantity"); changed = "job"
        elif mode == "wrong-job-record-type":
            job["length"]["value"] = "100"; changed = "job"
        elif mode == "rewired-context":
            main["steps"]["mass"]["in"]["context"] = {"default": {"class": "File", "path": "other-context.json"}}; changed = "workflow"
        elif mode == "adapter-signature":
            tool = next(entry for entry in workflow["$graph"] if entry["id"] == "#mcp-call")
            tool["inputs"]["node"]["inputBinding"]["prefix"] = "--different-node"; changed = "workflow"
        elif mode == "adapter-extra-arguments":
            tool = next(entry for entry in workflow["$graph"] if entry["id"] == "#mcp-call")
            tool["arguments"] = ["--undeclared-control", "unexpected"]; changed = "workflow"
        elif mode == "bad-output-source":
            main["outputs"]["mass_result"]["outputSource"] = "nonexistent/result"; changed = "workflow"
        elif mode in ("bad-output-glob", "missing-output-glob"):
            tool = deepcopy(next(entry for entry in workflow["$graph"] if entry["id"] == "#mcp-call"))
            tool["id"] = "#mass-call"
            if mode == "bad-output-glob": tool["outputs"]["result"]["outputBinding"]["glob"] = "missing-mass-output.json"
            else: tool["outputs"]["result"]["outputBinding"].pop("glob")
            workflow["$graph"].append(tool); main["steps"]["mass"]["run"] = "#mass-call"; changed = "workflow"
        elif mode == "schema-drift":
            contract = self.package / req["operations"]["main/mass"]["toolContract"]
            descriptor = read_json(contract)
            descriptor["inputSchema"]["properties"]["volume"]["properties"]["value"]["minimum"] = 1
            write_json(contract, descriptor)
        elif mode == "protocol-version":
            req["bindings"]["engineering"]["protocolVersion"] = "2026-07-28"; changed = "requirements"
        elif mode == "application-version":
            req["bindings"]["engineering"]["application"]["version"] = "99.0.0"; changed = "requirements"
        elif mode == "platform-unavailable":
            req["bindings"]["engineering"]["executionPlatforms"] = ["unavailable-mock-platform"]; changed = "requirements"
        elif mode == "missing-acceptance-field":
            next(c for c in req["acceptance"] if c["node"] == "main/mass")["valuePointer"] = "/structuredContent/noObservedMeasurement"; changed = "requirements"
        elif mode == "equivalent-input-units":
            for name in ("length", "width", "thickness"):
                job[name]["value"] /= 1000; job[name]["unit"] = "m"
            job["density"]["value"] /= 1000; job["density"]["unit"] = "g/cm3"; changed = "job"
        elif mode == "overflow-acceptance":
            for name in ("length", "width", "thickness"):
                job[name].update(value=1, unit="m")
            job["density"].update(value=1e308, unit="kg/m3")
            next(c for c in req["acceptance"] if c["node"] == "main/volume")["expected"] = 1
            mass = next(c for c in req["acceptance"] if c["node"] == "main/mass")
            mass.update(unit="g", expected=1e308, absoluteTolerance=0)
            write_json(requirement_file, req); changed = "job"
        elif mode == "unverifiable-resource":
            shim = ROOT / "tests" / "conformance" / "resource_revision_shim.py"
            req["bindings"]["engineering"]["implementation"].update(id="urn:engineering-process-spec:mock-mcp-unverifiable-resource", artifactSha256=digest(shim))
            req["process"]["revision"] += ".unverifiable-resource-test"
            changed = "requirements"
        elif mode in ("criterion-grams", "criterion-dimension", "criterion-unsupported"):
            criterion = next(c for c in req["acceptance"] if c["node"] == "main/mass")
            criterion["unit"] = {"criterion-grams": "g", "criterion-dimension": "mm", "criterion-unsupported": "unimplemented-unit"}[mode]
            if mode == "criterion-grams":
                criterion["expected"] *= 1000; criterion["absoluteTolerance"] *= 1000
            changed = "requirements"
        elif mode == "bad-tool-unit":
            job["length"]["unit"] = "kg"; changed = "job"
        elif mode == "nonfinite-job":
            job["length"]["value"] = float("nan")
            job_file.write_text(json.dumps(job, allow_nan=True), encoding="utf-8")
        elif mode == "corrupt-job":
            job_file.write_bytes(job_file.read_bytes() + b" ")
            return  # This case intentionally retains the old inventory digest.
        elif mode == "missing-job":
            job_file.unlink()
            return  # This case intentionally retains the missing payload's inventory entry.
        else:
            raise ValueError(f"Unknown fixture edit {mode}")
        if changed == "requirements": write_json(requirement_file, req)
        elif changed == "workflow": write_json(workflow_file, workflow)
        elif changed == "job": write_json(job_file, job)
        reinventory(self.package)

    def cli(self, command: str, source: Path | None = None, *, out: Path | None = None, bindings: Path | None = None, extra: list[str] | None = None) -> dict:
        prefix = [sys.executable, "-m", "epx.cli"] if self.implementation == "python" else [shutil.which("node") or "node", str(NODE_CLI)]
        argv = prefix + [command, str(source or self.package)]
        if command == "preserve" and self.implementation == "python":
            argv.append(str(out))
        elif out is not None:
            argv += ["--out", str(out)]
        if bindings is not None:
            argv += ["--bindings", str(bindings)]
        if command == "run":
            argv += ["--engine", "cwltool" if self.implementation == "python" else "streamflow"]
        argv += extra or []
        index = len(self.invocations) + 1
        prefix_path = self.root / f"cli-{index:02d}-{command}"
        env = os.environ.copy(); env["EPX_PYTHON"] = sys.executable
        started = time.monotonic()
        try:
            completed = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=self.timeout)
            return_code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout.decode("utf-8", errors="replace") if isinstance(error.stdout, bytes) else error.stdout or ""
            stderr = error.stderr.decode("utf-8", errors="replace") if isinstance(error.stderr, bytes) else error.stderr or ""
            return_code = None
        prefix_path.with_suffix(".stdout.json").write_text(stdout, encoding="utf-8")
        prefix_path.with_suffix(".stderr.log").write_text(stderr, encoding="utf-8")
        invocation = {"command": argv, "exitCode": return_code, "elapsedSeconds": round(time.monotonic() - started, 3), "stdout": prefix_path.with_suffix(".stdout.json").relative_to(self.root).as_posix(), "stderr": prefix_path.with_suffix(".stderr.log").relative_to(self.root).as_posix()}
        self.invocations.append(invocation)
        write_json(self.root / "commands.json", self.invocations)
        if return_code is None:
            raise CheckFailed(f"CLI exceeded {self.timeout} seconds: {argv}")
        try:
            output = json.loads(stdout)
        except ValueError as error:
            raise CheckFailed(f"CLI stdout is not its public JSON response; inspect {invocation['stdout']} and {invocation['stderr']}") from error
        def finite_json(value):
            if isinstance(value, float): return math.isfinite(value)
            if isinstance(value, dict): return all(finite_json(item) for item in value.values())
            if isinstance(value, list): return all(finite_json(item) for item in value)
            return True
        self.check("Public response contains only finite JSON numbers", finite_json(output))
        self.check(f"{command} returns a JSON object", isinstance(output, dict))
        if command in ("inspect", "validate") and is_valid(output):
            self.check("Valid inspect/validate result exits successfully", return_code, 0)
        return {"exitCode": return_code, "value": output}

    def audit_events(self, event: str | None = None) -> list[dict]:
        rows = [] if not self.audit.exists() else [json.loads(line) for line in self.audit.read_text(encoding="utf-8").splitlines()]
        return rows if event is None else [row for row in rows if row["event"] == event]

    def zero_calls(self) -> None:
        self.check("No engineering calls were made", len(self.audit_events("tool_call")), 0)
        self.check("No mutation was made", len(self.audit_events("mutation")), 0)

    def diagnostics(self, value: dict, category: str | None = None, code: str | None = None) -> list[dict]:
        diagnostics = value.get("diagnostics", [])
        self.check("Structured diagnostics are present", isinstance(diagnostics, list) and len(diagnostics) > 0)
        for detail in diagnostics:
            self.check("Diagnostic identifies code/category/requirement/message", all(isinstance(detail.get(key), str) and detail[key] for key in ("code", "category", "requirement", "message")))
        if category:
            self.check("Expected diagnostic category is retained", category in {detail["category"] for detail in diagnostics})
        if code:
            translated = code
            if self.implementation == "python":
                translated = {"EPX_RESOURCE_ABSENT": "RESOURCE_UNAVAILABLE", "EPX_RESOURCE_DENIED": "RESOURCE_UNAVAILABLE", "EPX_OUTPUT_INVALID": "TOOL_RESULT_INVALID"}.get(code, code.removeprefix("EPX_"))
            self.check("Expected distinct diagnostic cause is retained", translated in {detail["code"] for detail in diagnostics})
            if code in ("EPX_RESOURCE_ABSENT", "EPX_RESOURCE_DENIED"):
                native = -32002 if code == "EPX_RESOURCE_ABSENT" else -32003
                self.check("Resource absence/denial retains the actual protocol cause", any(detail.get("cause", {}).get("code") == native for detail in diagnostics if isinstance(detail.get("cause"), dict)))
        return diagnostics

    def preserved(self, source: Path | None = None, destination: Path | None = None) -> None:
        source = source or self.package
        destination = destination or self.root / "preserved"
        before = digest(source) if source.is_file() else tree_digests(source)
        copied = self.cli("preserve", source, out=destination)
        self.check("Preserve CLI succeeded", copied["exitCode"], 0)
        after = digest(destination) if destination.is_file() else tree_digests(destination)
        self.check("Preserved bytes match every original file", after, before)

    def assert_run(self, report: dict, expected: dict | None = None, package: Path | None = None, run_directory: Path | None = None) -> None:
        expected = expected or self.spec; package = package or self.package; run_directory = run_directory or self.run_directory
        errors = [error.message for error in Draft202012Validator(read_json(ROOT / "schemas" / "run.schema.json")).iter_errors(report)]
        self.check("Run report satisfies shared structural schema", errors, [])
        self.check("Run report identifies its exact profile", report.get("profile"), PROFILE)
        self.check("Report equals persisted public report", read_json(run_directory / "report.json"), report)
        self.check("Report identifies exact metadata bytes", report["packageMetadataSha256"], digest(package / "ro-crate-metadata.json"))
        self.check("Report identifies exact job bytes", report.get("inputSha256"), digest(package / "inputs" / "job.json"))
        self.check("Report identifies exact process revision", report["process"], read_json(package / "requirements.json")["process"])
        self.check("Execution outcome matches observed case", report["execution"]["status"], expected["execution"])
        self.check("Acceptance is separate and correctly classified", report["acceptance"]["status"], expected["acceptance"])
        self.check("No human approval is invented", report["approval"], "not-requested")
        self.check("Engine identity names the independent path", report["engine"]["name"].lower(), "cwltool" if self.implementation == "python" else "streamflow")
        self.check("Engine version is explicit", isinstance(report["engine"].get("version"), str) and bool(report["engine"]["version"]))
        successful = [call for call in report["calls"] if call["status"] == "succeeded"]
        self.check("Exactly the expected nodes succeeded", sorted(call["node"] for call in successful), sorted(expected["successfulNodes"]))
        self.check("Actual provider tool-call count matches", len(self.audit_events("tool_call")), expected["toolCalls"])
        self.check("Actual mutation count matches; read-only calls do not mutate and mutations are not replayed", len(self.audit_events("mutation")), expected.get("mutations", 0))
        for call in report["calls"]:
            self.check("Call is tied to this run and package", [call["runId"], call.get("packageMetadataSha256")], [report["runId"], report["packageMetadataSha256"]])
            if call["status"] == "succeeded":
                self.check("Successful call has observed intended provider", call.get("observedProvider", {}).get("application"), read_json(package / "requirements.json")["bindings"][call["binding"]]["application"]["id"])
                self.check("Successful call has raw MCP result evidence", isinstance(call.get("result"), dict) and "structuredContent" in call["result"])
                measurement = call["result"]["structuredContent"]
                if call["node"] == "main/volume":
                    oracle = self.spec.get("observedResults", {}).get(call["node"], {"quantity": "volume", "value": 0.00002, "unit": "m3"})
                    self.check("Volume is independently expected from the authored dimensions", measurement, oracle)
                elif call["node"] == "main/mass":
                    mass = 157.0 if self.spec.get("fault") == "wrong-value" else 0.157
                    oracle = self.spec.get("observedResults", {}).get(call["node"], {"quantity": "mass", "value": mass, "unit": "kg"})
                    self.check("Mass result retains the actual observed quantity", measurement, oracle)
                request = call.get("request", {})
                arguments = request.get("params", {}).get("arguments")
                tool = request.get("params", {}).get("name")
                self.check("Call evidence matches an actual provider-observed request", any(row["name"] == tool and row["arguments"] == arguments for row in self.audit_events("tool_call")))
            if "artifact" in call:
                artifact = call["artifact"]
                path = (run_directory / artifact["path"]).resolve()
                self.check("Evidence artifact stays inside its run", path.is_relative_to(run_directory.resolve()))
                self.check("Retained output digest matches bytes", digest(path), artifact["sha256"])
                if "result" in call:
                    self.check("Retained output matches original MCP result", read_json(path), call["result"])
        transform = report.get("transformation", {})
        self.check("Derived execution copy records original workflow digest", transform.get("sourceSha256"), digest(package / "workflow.cwl.json"))
        self.check("Derived workflow has a separate digest", isinstance(transform.get("derivedSha256"), str) and transform.get("derivedSha256") != transform.get("sourceSha256"))
        if expected.get("diagnosticCode"):
            self.diagnostics(report, code=expected["diagnosticCode"])
        if expected["execution"] == "unknown":
            self.diagnostics(report, category="outcome-unknown")
            self.check("Exactly one unknown operation is retained", len([call for call in report["calls"] if call["status"] == "unknown"]), 1)
        elif expected["execution"] == "failed":
            self.check("Failed execution retains a cause", bool(report["diagnostics"]))
        for criterion in report["acceptance"]["criteria"]:
            if criterion["status"] == "pass":
                matches = [call for call in successful if call["node"] == criterion.get("node")]
                self.check("Passed criterion resolves one successful producing call", len(matches), 1)
                evidence_sha = criterion.get("artifactSha256") or criterion.get("evidence", {}).get("artifact", {}).get("sha256")
                self.check("Passed criterion identifies the observed result artifact", evidence_sha, matches[0]["artifact"]["sha256"])

    def check_unchanged(self) -> None:
        self.check("Original repository example was not modified", tree_digests(self.package_source), self.original_source)
        self.check("CLI did not alter the prepared process package", tree_digests(self.package), self.prepared_package)


def run_case(context: CaseContext) -> None:
    action = context.spec["action"]
    if action == "preserve-missing":
        write_json(context.bindings_file, {"format": "epx-bindings", "version": VERSION, "bindings": {}})
        inspection = context.cli("inspect")
        context.check("Provider absence does not invalidate definition", is_valid(inspection["value"]))
        context.check("Inspection claims no engineering calls", inspection["value"].get("engineeringCalls"), 0)
        unavailable = context.cli("preflight", bindings=context.bindings_file)
        context.check("Missing provider is unavailable", unavailable["value"].get("status"), "unavailable")
        context.diagnostics(unavailable["value"], "unavailable")
        context.preserved(); context.zero_calls()
    elif action in ("preserve-zip", "reject-zip"):
        archive = context.root / "received.zip"
        escape_name = "epx-escape-" + uuid.uuid4().hex
        escaped = Path(tempfile.gettempdir()) / escape_name
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as stream:
            for file in sorted(context.package.rglob("*")):
                if file.is_file(): stream.write(file, file.relative_to(context.package).as_posix())
            fault = context.spec.get("zipFault")
            if fault == "traversal": stream.writestr("../" + escape_name, b"must not be materialized")
            elif fault == "duplicate": stream.writestr("requirements.json", b"{}")
            elif fault == "symlink":
                member = zipfile.ZipInfo("symlink.txt"); member.create_system = 3; member.external_attr = 0o120777 << 16
                stream.writestr(member, "../" + escape_name)
        checked = context.cli("validate", archive)
        if action == "preserve-zip":
            context.check("ZIP is interpreted as a valid process", is_valid(checked["value"]))
        else:
            context.check("Unsafe archive was rejected", checked["exitCode"] != 0)
            context.diagnostics(checked["value"], "invalid")
            context.check("Archive did not materialize an escaping file", escaped.exists(), False)
        context.preserved(archive, context.root / "preserved.zip"); context.zero_calls()
    elif action == "optional-metadata":
        reqfile = context.package / "requirements.json"; req = read_json(reqfile)
        req.setdefault("extensions", {})["urn:engineering-process-spec:unknown-optional"] = {"unfamiliar": ["α", {"setting": "preserve exactly"}], "graphMeaning": "none"}
        write_json(reqfile, req); reinventory(context.package); context.prepared_package = tree_digests(context.package)
        checked = context.cli("inspect"); context.check("Unknown optional metadata is accepted", is_valid(checked["value"]))
        context.preserved(); context.zero_calls()
    elif action == "reject":
        checked = context.cli("validate")
        context.check("Invalid/unsupported process is not accepted", checked["exitCode"] != 0)
        context.check("Validation never claims valid", is_valid(checked["value"]), False)
        context.diagnostics(checked["value"], context.spec["category"])
        if context.spec.get("attemptRun"):
            attempted = context.cli("run", out=context.run_directory, bindings=context.bindings_file)
            context.check("Invalid default job cannot execute", attempted["exitCode"] != 0)
            context.diagnostics(attempted["value"], "invalid")
        context.preserved(); context.zero_calls()
    elif action == "preflight-reject":
        checked = context.cli("validate")
        context.check("Unavailable environment leaves understood definition valid", is_valid(checked["value"]))
        ready = context.cli("preflight", bindings=context.bindings_file)
        context.check("Unavailable dependency is not preflight success", ready["exitCode"] != 0)
        context.diagnostics(ready["value"], context.spec["category"], context.spec.get("diagnosticCode"))
        if context.spec.get("edit") == "unverifiable-resource":
            context.check("The actual observed resource revision was deliberately omitted", bool(context.audit_events("resource_revision_omitted")))
        blocked = context.cli("run", out=context.run_directory, bindings=context.bindings_file)
        context.check("Unavailable prerequisite blocks execution", blocked["value"].get("execution", {}).get("status"), "blocked")
        context.check("No acceptance performed on blocked execution", blocked["value"]["acceptance"]["status"], "not-run")
        context.check("No calls recorded for blocked execution", blocked["value"]["calls"], [])
        context.preserved(); context.zero_calls()
    elif action == "run":
        executed = context.cli("run", out=context.run_directory, bindings=context.bindings_file)
        context.assert_run(executed["value"])
        if context.spec["execution"] != "succeeded" or context.spec["acceptance"] != "pass":
            context.check("Failure is reflected in CLI exit status", executed["exitCode"] != 0)
        elif context.spec["acceptance"] == "pass":
            context.check("Successful execution and acceptance exit cleanly", executed["exitCode"], 0)
    elif action == "rebind":
        first = context.cli("preflight", bindings=context.bindings_file)
        context.check("Original explicit binding is available", is_available(first["value"]))
        relocated = context.root / "different installation" / "mock_mcp_server.py"
        relocated.parent.mkdir(); shutil.copyfile(PROVIDER, relocated)
        binding = context.bindings["bindings"]["engineering"]
        binding["transport"]["arguments"][0] = str(relocated)
        binding["trust"]["path"] = str(relocated)
        write_json(context.bindings_file, context.bindings)
        second = context.cli("preflight", bindings=context.bindings_file)
        context.check("Same verified bytes at a new local path remain available", is_available(second["value"]))
        context.check("Local rebinding leaves all process bytes unchanged", tree_digests(context.package), context.prepared_package)
        context.zero_calls()
        executed = context.cli("run", out=context.run_directory, bindings=context.bindings_file)
        context.assert_run(executed["value"], {"execution": "succeeded", "acceptance": "pass", "successfulNodes": ["main/volume", "main/mass"], "toolCalls": 2})
    elif action == "replacement":
        replacement_binding = context.bindings["bindings"]["engineering"]
        replacement_binding["application"]["id"] = NEW_APPLICATION
        replacement_binding["transport"]["arguments"] += ["--application", NEW_APPLICATION]
        write_json(context.bindings_file, context.bindings)
        refused = context.cli("preflight", bindings=context.bindings_file)
        context.check("Another provider cannot act as local rebinding", refused["exitCode"] != 0)
        context.diagnostics(refused["value"], "unavailable"); context.zero_calls()
        replacement = context.root / "explicit-replacement"
        requirements = read_json(context.package / "requirements.json")
        old_revision = requirements["process"]["revision"]
        descriptor = deepcopy(requirements["bindings"]["engineering"])
        descriptor["application"]["id"] = NEW_APPLICATION
        descriptor_path = context.root / "explicit-intended-provider.json"
        write_json(descriptor_path, descriptor)
        replaced = context.cli("replace", out=replacement, extra=["--binding", "engineering", "--with", str(descriptor_path), "--revision", old_revision + ".explicit-replacement"])
        context.check("Explicit provider replacement command succeeds", replaced["exitCode"], 0)
        context.check("Replacement makes no engineering calls", replaced["value"].get("engineeringCalls"), 0)
        context.zero_calls()
        requirements = read_json(replacement / "requirements.json")
        context.check("Replacement records the intended new provider", requirements["bindings"]["engineering"], descriptor)
        change = replaced["value"].get("change", replaced["value"])
        impacted = change.get("acceptanceRequiresRerun", change.get("impactedAcceptance"))
        context.check("Replacement invalidates affected acceptance", sorted(impacted), sorted(item["id"] for item in requirements["acceptance"]))
        prior = change.get("previousRequirements")
        prior_path = prior["path"] if isinstance(prior, dict) else prior
        context.check("Replacement retains exact prior requirements", digest(replacement / prior_path), digest(context.package / "requirements.json"))
        context.check("Replacement does not claim provider equivalence", change.get("providerEquivalenceClaimed", change.get("engineeringEquivalence") != "not-established"), False)
        for path, before in context.prepared_package.items():
            if path not in ("requirements.json", "ro-crate-metadata.json"):
                context.check("Unaffected replacement payload retains identity: " + path, digest(replacement / path), before)
        context.check("Replacement is a new process revision", requirements["process"]["revision"] != old_revision)
        checked = context.cli("validate", replacement); context.check("Explicit revision validates against its new intended provider", is_valid(checked["value"]))
        executed = context.cli("run", replacement, out=context.run_directory, bindings=context.bindings_file)
        context.assert_run(executed["value"], {"execution": "succeeded", "acceptance": "pass", "successfulNodes": ["main/volume", "main/mass"], "toolCalls": 2}, replacement)
    elif action == "http":
        run_http_case(context)
    elif action == "output-contract":
        result = context.cli("run", out=context.run_directory, bindings=context.bindings_file)
        context.check("Broken declared CWL output is not successful execution", result["exitCode"] != 0)
        if "execution" in result["value"]:
            context.check("A call record alone cannot imply workflow output completion", result["value"]["execution"]["status"], "failed")
            context.diagnostics(result["value"], "execution-failed")
            context.check("Read-only output test made no mutation", len(context.audit_events("mutation")), 0)
        else:
            context.check("Invalid output contract is not accepted", is_valid(result["value"]), False)
            context.diagnostics(result["value"], "invalid"); context.zero_calls()
    elif action == "nonoverwrite":
        context.run_directory.mkdir(); sentinel = context.run_directory / "prior-evidence.txt"; sentinel.write_text("retain prior evidence", encoding="utf-8")
        before = digest(sentinel)
        result = context.cli("run", out=context.run_directory, bindings=context.bindings_file)
        context.check("Nonempty run directory is rejected", result["exitCode"] != 0)
        context.check("Existing evidence unchanged", digest(sentinel), before)
        context.diagnostics(result["value"], "invalid"); context.zero_calls()
    else:
        raise ValueError(f"No runner for action {action}")
    context.check_unchanged()


def run_http_case(context: CaseContext) -> None:
    target = "mock-target-independent-of-client-platform"
    requirements_file = context.package / "requirements.json"; requirements = read_json(requirements_file)
    requirements["bindings"]["engineering"]["executionPlatforms"] = [target]
    write_json(requirements_file, requirements); reinventory(context.package); context.prepared_package = tree_digests(context.package)
    argv = [sys.executable, "-u", str(PROVIDER), "--http-port", "0", "--execution-platform", target, "--audit", str(context.audit)]
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    ready: Queue = Queue(); Thread(target=lambda: ready.put(process.stderr.readline()), daemon=True).start()
    try:
        try: readiness_line = ready.get(timeout=5)
        except Empty as error: raise CheckFailed("Mock HTTP provider did not become ready") from error
        readiness = json.loads(readiness_line)
        context.check("HTTP provider reports readiness", readiness.get("event"), "listening")
        (context.root / "http-readiness.json").write_text(readiness_line, encoding="utf-8")
        binding = context.bindings["bindings"]["engineering"]
        binding["transport"] = {"kind": "http", "url": readiness["url"]}
        binding["trust"] = {"kind": "configured-service", "subject": requirements["bindings"]["engineering"]["implementation"]["id"], "description": "Controlled harness-launched loopback mock, with source digest recorded; not an authenticated remote CAD service."}
        write_json(context.bindings_file, context.bindings)
        preflight = context.cli("preflight", bindings=context.bindings_file)
        context.check("Target metadata is accepted over an actual HTTP connection", is_available(preflight["value"]))
        context.zero_calls()
        context.check("Target platform differs from client OS identity", target != sys.platform)
        executed = context.cli("run", out=context.run_directory, bindings=context.bindings_file)
        context.assert_run(executed["value"], {"execution": "succeeded", "acceptance": "pass", "successfulNodes": ["main/volume", "main/mass"], "toolCalls": 2})
        write_json(context.root / "http-scope.json", {"command": argv, "serverSha256": digest(PROVIDER), "transport": "actual loopback HTTP", "clientPlatform": sys.platform, "controlledTargetDeclaration": target, "actualCrossOSExecutionClaim": False})
    finally:
        process.terminate()
        try: process.wait(timeout=3)
        except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=3)
        (context.root / "http.stdout.log").write_text(process.stdout.read(), encoding="utf-8")
        (context.root / "http.stderr.log").write_text(process.stderr.read(), encoding="utf-8")
        process.stdout.close(); process.stderr.close()


def package_version(name: str) -> str | None:
    try: return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError: return None


def installed_artifacts() -> dict:
    """Identify installed wheel contents, not merely a mutable version label."""
    try:
        distribution = importlib.metadata.distribution("engineering-process-kit")
    except importlib.metadata.PackageNotFoundError:
        return {"status": "not-installed"}
    files = {}
    origin = None
    for item in distribution.files or []:
        path = distribution.locate_file(item)
        if path.is_file() and (path.suffix in (".py", ".json") or path.name in ("METADATA", "RECORD", "entry_points.txt")):
            files[str(item)] = digest(path)
        if path.name == "direct_url.json" and path.is_file():
            origin = read_json(path)
    return {"status": "installed", "version": distribution.version, "filesSha256": files, "installOrigin": origin}


def node_artifacts() -> dict:
    paths = list(NODE_CLI.parent.glob("*.mjs")) + list(NODE_CLI.parent.glob("package*.json")) + list(NODE_CLI.parent.glob("schemas/*.json"))
    result = {"entrypoint": str(NODE_CLI), "filesSha256": {str(path): digest(path) for path in sorted(paths)}}
    result["resolvedDependencies"] = {}
    metadata = read_json(NODE_CLI.parent / "package.json")
    for name in metadata.get("dependencies", {}):
        dependency = NODE_CLI.parent / "node_modules" / name / "package.json"
        if dependency.is_file():
            installed = read_json(dependency)
            result["resolvedDependencies"][name] = {"version": installed["version"], "packageJsonSha256": digest(dependency)}
        else:
            result["resolvedDependencies"][name] = {"status": "not-located-at-application-node_modules"}
    archive = os.environ.get("EPX_NODE_ARCHIVE")
    if archive:
        matches = {}
        with tarfile.open(archive, "r:gz") as stream:
            for entry in stream.getmembers():
                if entry.isfile() and entry.name.startswith("package/"):
                    content = stream.extractfile(entry).read()
                    installed = NODE_CLI.parent / entry.name.removeprefix("package/")
                    matches[entry.name] = installed.is_file() and digest(installed) == hashlib.sha256(content).hexdigest()
        result["archive"] = {"path": archive, "sha256": digest(Path(archive)), "installedFilesMatch": matches, "allMatch": bool(matches) and all(matches.values())}
    return result


def command_observation(argv: list[str]) -> dict:
    try:
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=10)
        return {"command": argv, "exitCode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"command": argv, "exitCode": None, "reason": str(error)}


def requirement_coverage(catalog: dict, cases: list[dict], implementations: list[str]) -> dict:
    requirements = re.findall(r"\*\*([A-Z]+-\d{3})\s+—", (ROOT / "spec" / "core-draft.md").read_text(encoding="utf-8"))
    by_implementation = {}
    for implementation in implementations:
        outcomes = {case["id"]: case for case in cases if case["implementation"] == implementation}
        coverage = {}
        for requirement in requirements:
            applicable = [case for case in catalog["cases"] if case["mandatory"] and requirement in case["requirements"]]
            statuses = [outcomes.get(case["id"], {"status": "not run"})["status"] for case in applicable]
            status = "failed" if "failed" in statuses else "unsupported" if "unsupported" in statuses else "not run" if not applicable or "not run" in statuses else "passed"
            coverage[requirement] = {"status": status, "cases": [case["id"] for case in applicable], "scope": "Mapped observable assertions only; see case evidence and scope limitations."}
        by_implementation[implementation] = coverage
    return by_implementation


def execute_case(spec: dict, implementation: str, out: Path, timeout: int) -> dict:
    case = {"id": spec["id"], "title": spec["title"], "implementation": implementation, "roles": spec["roles"], "requirements": spec["requirements"], "scope": spec["scope"], "mandatory": spec["mandatory"], "status": "not run"}
    if spec["action"] == "later":
        case["reason"] = spec["reason"]
        return case
    context = None
    try:
        context = CaseContext(spec, implementation, out / implementation / spec["id"], timeout)
        run_case(context)
        case["status"] = "passed"
    except Exception as error:
        case["status"] = "failed"; case["reason"] = str(error); case["traceback"] = traceback.format_exc()
    if context:
        case["evidenceDirectory"] = context.root.relative_to(out).as_posix()
        case["checks"] = context.checks
        case["invocations"] = context.invocations
        write_json(context.root / "case-result.json", case)
    return case


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="New or empty evidence directory; never overwrite old reports")
    parser.add_argument("--implementation", choices=["python", "node", "both"], default="both")
    parser.add_argument("--case", action="append", dest="cases", help="Run one listed case; repeat for targeted debugging")
    parser.add_argument("--timeout", type=int, default=180, help="Per public CLI invocation timeout in seconds")
    parser.add_argument("--jobs", type=int, default=1, help="Independent case workers; each retains separate packages, runs, and provider audits")
    parser.add_argument("--list", action="store_true", help="List the catalog without invoking applications")
    options = parser.parse_args()
    catalog = read_json(CATALOG)
    if options.list:
        print(json.dumps(catalog, indent=2)); return 0
    if options.out is None: parser.error("--out is required")
    if options.timeout < 1: parser.error("--timeout must be positive")
    if options.jobs < 1 or options.jobs > 8: parser.error("--jobs must be between 1 and 8")
    selected = set(options.cases or [case["id"] for case in catalog["cases"]])
    unknown = selected - {case["id"] for case in catalog["cases"]}
    if unknown: parser.error("Unknown case IDs: " + ", ".join(sorted(unknown)))
    out = options.out.resolve()
    if out.exists() and any(out.iterdir()): parser.error("--out must be new or empty; retain earlier evidence")
    out.mkdir(parents=True, exist_ok=True)
    implementations = ["python", "node"] if options.implementation == "both" else [options.implementation]
    starting_sources = source_snapshot()
    report = {
        "format": "epx-conformance-report", "version": VERSION, "suite": catalog["suite"], "profile": PROFILE,
        "startedAt": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
        "platform": {"system": platform.platform(), "python": sys.version, "clientPlatform": sys.platform},
        "containerImage": os.environ.get("EPX_CONTAINER_IMAGE_ID"),
        "dependencies": {name: package_version(name) for name in ("engineering-process-kit", "cwltool", "streamflow", "jsonschema", "cwl-utils", "schema-salad")},
        "node": command_observation([shutil.which("node") or "node", "--version"]),
        "repository": command_observation(["git", "-c", f"safe.directory={ROOT}", "rev-parse", "HEAD"]),
        "sourceSnapshotBefore": starting_sources, "claimedRoles": SUPPORTED_ROLES,
        "roleLimitations": {"editor": "Byte-preserving save and explicit provider replacement only; no general editing UI or transformation equivalence is claimed."},
        "installedPythonArtifactBefore": installed_artifacts(),
        "nodeArtifactBefore": node_artifacts(),
        "scopeLimitations": [
            "A finite fixture suite demonstrates its listed behaviors, not all possible upstream CWL/MCP behavior.",
            "The two paths share schemas/fixtures and may share upstream parsing libraries; their CLI/interpreter/resolver/adapter identities are recorded separately.",
            "Editor evidence is limited to byte-preserving save and explicit provider replacement through public CLIs; no general editor UI is claimed.",
            "B05 uses actual loopback HTTP with controlled target-platform metadata, not actual cross-OS CAD execution or authenticated service identity.",
            "Real Solid Edge and richer human approval remain outside this mock core and are never counted as passed.",
        ],
        "cases": [],
    }
    all_mandatory_passed = True
    with ThreadPoolExecutor(max_workers=options.jobs) as pool:
        futures = [pool.submit(execute_case, spec, implementation, out, options.timeout) for implementation in implementations for spec in catalog["cases"] if spec["id"] in selected]
        for future in as_completed(futures):
            case = future.result()
            if case["mandatory"] and case["status"] != "passed": all_mandatory_passed = False
            report["cases"].append(case)
            print(f"{case['implementation']} {case['id']}: {case['status']}" + (f" — {case['reason']}" if "reason" in case else ""), flush=True)
            write_json(out / "report.json", report)
    report["cases"].sort(key=lambda case: (case["implementation"], case["id"]))
    report["completedAt"] = datetime.now(timezone.utc).isoformat()
    report["sourceSnapshotAfter"] = source_snapshot()
    report["sourcesStableDuringRun"] = starting_sources == report["sourceSnapshotAfter"]
    report["installedPythonArtifactAfter"] = installed_artifacts()
    report["nodeArtifactAfter"] = node_artifacts()
    report["installedArtifactStableDuringRun"] = report["installedPythonArtifactBefore"] == report["installedPythonArtifactAfter"] and report["nodeArtifactBefore"] == report["nodeArtifactAfter"]
    report["requirementCoverage"] = requirement_coverage(catalog, report["cases"], implementations)
    report["counts"] = {status: sum(case["status"] == status for case in report["cases"]) for status in ("passed", "failed", "unsupported", "not run")}
    complete_selection = selected >= {case["id"] for case in catalog["cases"] if case["mandatory"]}
    report["fullCoreSelected"] = complete_selection
    coverage_complete = all(item["status"] == "passed" for requirements in report["requirementCoverage"].values() for item in requirements.values())
    artifact_verified = report["nodeArtifactBefore"].get("archive", {}).get("allMatch", True)
    report["coreConformanceDemonstrated"] = all_mandatory_passed and coverage_complete and complete_selection and report["sourcesStableDuringRun"] and report["installedArtifactStableDuringRun"] and artifact_verified and len(implementations) == 2
    report["summary"] = "Required selected cases passed" if all_mandatory_passed else "Mandatory selected cases failed; inspect evidence before any conformance claim"
    if not report["sourcesStableDuringRun"]:
        report["summary"] += "; implementation/spec/suite sources changed during this run, so repeat against a fixed revision"
    write_json(out / "report.json", report)
    print(json.dumps({"report": str(out / "report.json"), "counts": report["counts"], "coreConformanceDemonstrated": report["coreConformanceDemonstrated"], "sourcesStableDuringRun": report["sourcesStableDuringRun"]}))
    return 0 if all_mandatory_passed and report["sourcesStableDuringRun"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
