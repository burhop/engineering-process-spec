"""Prepare a preserving execution snapshot and invoke an existing CWL engine."""

from __future__ import annotations

from importlib import metadata
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from urllib.parse import unquote, urlparse

from . import IMPLEMENTATION, PROFILE, VERSION
from . import acceptance, jsonio, mcp
from .errors import Problem, invalid
from .package import load, open_root

ENGINE_VERSIONS = {"cwltool": "3.2.20260720092025", "streamflow": "0.2.0rc2"}


def _verify_engine_outputs(package, raw, calls):
    try:
        outputs = jsonio.loads(raw)
        if not isinstance(outputs, dict):
            raise ValueError("Engine did not return a workflow-output object")
        for output_name, declaration in package.main["outputs"].items():
            file = outputs[output_name]
            if file.get("class") != "File":
                raise ValueError(f"Missing required File output {output_name}")
            locator = file.get("path", file.get("location"))
            if not isinstance(locator, str):
                raise ValueError(f"Missing output location {output_name}")
            if locator.startswith("file:"):
                location = unquote(urlparse(locator).path)
                if os.name == "nt" and location.startswith("/") and len(location) > 2 and location[2] == ":":
                    location = location[1:]
                path = Path(location)
            else:
                path = Path(locator)
            sha256 = jsonio.digest(path.read_bytes())
            node = "main/" + declaration["outputSource"].split("/")[0]
            matches = [call for call in calls if call.get("node") == node and call.get("status") == "succeeded"]
            if len(matches) != 1 or sha256 != matches[0].get("resultSha256"):
                raise ValueError(f"Engine output {output_name} differs from its observed MCP result")
        return outputs
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise Problem("WORKFLOW_OUTPUT_MISSING", "execution-failed", "CWL-005", "Required workflow outputs were not materialized from observed call results", cause=str(exc)) from exc


def _stage_inputs(value, base, artifacts):
    if isinstance(value, list):
        return [_stage_inputs(item, base, artifacts) for item in value]
    if isinstance(value, dict):
        value = dict(value)
        if value.get("class") == "File":
            locator = value.get("path", value.get("location"))
            if not isinstance(locator, str) or "://" in locator:
                raise invalid("INPUT_FILE", "RES-001", "Input File needs an explicit available local path")
            path = Path(locator)
            if not path.is_absolute():
                path = base / path
            path = path.resolve()
            if not path.is_file():
                raise invalid("INPUT_FILE", "RES-001", "Input File is unavailable", path=str(path))
            value.pop("location", None)
            value["path"] = str(path)
            artifacts.append({"path": str(path), "sha256": jsonio.digest(path.read_bytes())})
        return {key: _stage_inputs(item, base, artifacts) for key, item in value.items()}
    return value


def run(source, bindings_path, output, engine="cwltool", job_path=None):
    output = Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise invalid("RUN_DESTINATION", "OUT-001", "A fresh empty run directory is required", path=str(output))
    with open_root(source) as original_root:
        if output.is_relative_to(original_root):
            raise invalid("RUN_DESTINATION", "PKG-004", "Run output must be outside the source package")
        original = load(original_root)
        output.mkdir(parents=True, exist_ok=True)
        run_id = str(uuid.uuid4())
        report = {
            "format": "epx-run", "version": VERSION, "profile": PROFILE, "implementation": IMPLEMENTATION,
            "runId": run_id, "process": original.requirements["process"],
            "packageMetadataSha256": original.metadata_sha256,
            "execution": {"status": "blocked"},
            "acceptance": {"status": "not-run", "criteria": []}, "approval": "not-requested",
            "calls": [], "outputs": [], "diagnostics": [],
            "engine": {"name": engine, "exitCode": None},
            "runtime": {"python": sys.version.split()[0], "platform": sys.platform},
        }
        package = original
        try:
            bindings_path = Path(bindings_path).resolve()
            config = mcp.configuration(bindings_path)
            report["preflight"] = mcp.preflight(original, config)
            if engine not in ENGINE_VERSIONS:
                raise Problem("ENGINE_UNSUPPORTED", "unsupported", "CWL-001", "Engine is not in the tested execution profile", observed=engine)
            try:
                actual_version = metadata.version(engine)
            except metadata.PackageNotFoundError as exc:
                raise Problem("ENGINE_UNAVAILABLE", "unavailable", "CWL-001", "The selected existing CWL engine is not installed", dependency=engine) from exc
            report["engine"]["version"] = actual_version
            if actual_version != ENGINE_VERSIONS[engine]:
                raise Problem("ENGINE_VERSION", "unavailable", "CWL-001", "Engine version is outside the tested profile", expected=ENGINE_VERSIONS[engine], observed=actual_version)
            # Keep original package bytes. Only a separately identified derived
            # workflow consumes the implemented exchange requirement.
            snapshot = output / "package"
            for path in original_root.rglob("*"):
                if path.is_symlink():
                    raise invalid("PACKAGE_PATH", "PKG-001", "Cannot snapshot a package symlink", path=str(path))
            shutil.copytree(original_root, snapshot)
            package = load(snapshot)
            derived = snapshot / "execution.cwl.json"
            jsonio.write(derived, package.execution_document())
            report["transformation"] = {
                "sourceSha256": package.inventory[package.workflow_path],
                "derivedSha256": jsonio.digest(derived.read_bytes()),
                "consumedRequirement": "epx:ExchangeRequirement",
            }
            context = {
                "format": "epx-run-context", "version": VERSION, "package": str(snapshot),
                "bindings": str(bindings_path), "runId": run_id, "runDirectory": str(output),
                "implementation": IMPLEMENTATION, "packageMetadataSha256": package.metadata_sha256,
            }
            context_path = output / "private" / "context.json"
            jsonio.write(context_path, context)
            job_source = Path(job_path).resolve() if job_path else package.payload(package.requirements["job"])
            inputs = jsonio.read(job_source)
            if not isinstance(inputs, dict) or "epx_context" in inputs:
                raise invalid("CONTEXT_INPUT", "CWL-004", "Portable input jobs cannot supply receiving execution context")
            from .inputs import validate_job
            validate_job(package.main, inputs)
            report["inputSha256"] = jsonio.digest(job_source.read_bytes())
            input_artifacts = []
            inputs = _stage_inputs(inputs, job_source.parent, input_artifacts)
            report["inputArtifacts"] = input_artifacts
            inputs["epx_context"] = {"class": "File", "path": str(context_path)}
            prepared_job = output / "private" / "job.json"
            jsonio.write(prepared_job, inputs)
            bin_path = output / "bin"
            bin_path.mkdir()
            if os.name == "nt":
                shim = bin_path / "epx-mcp-call.cmd"
                shim.write_text(f'@"{sys.executable}" -m epx.adapter %*\n', encoding="utf-8")
            else:
                import shlex
                shim = bin_path / "epx-mcp-call"
                shim.write_text("#!/bin/sh\nexec " + shlex.quote(sys.executable) + ' -m epx.adapter "$@"\n', encoding="utf-8")
                shim.chmod(0o755)
            env = dict(os.environ)
            env["PATH"] = str(bin_path) + os.pathsep + env.get("PATH", "")
            engine_output = output / "engine-output"
            if engine == "cwltool":
                command = [sys.executable, "-m", "cwltool", "--no-container", "--outdir", str(engine_output), str(derived) + "#main", str(prepared_job)]
            else:
                command = [sys.executable, "-c", "from streamflow.cwl.runner import run; run()", "--outdir", str(engine_output), str(derived) + "#main", str(prepared_job)]
            result = subprocess.run(command, env=env, capture_output=True, timeout=180)
            (output / "engine-stdout.log").write_bytes(result.stdout)
            (output / "engine-stderr.log").write_bytes(result.stderr)
            report["engine"]["exitCode"] = result.returncode
            report["calls"] = [jsonio.read(path) for path in sorted((output / "calls").glob("*.json"))]
            for call in report["calls"]:
                report["diagnostics"].extend(call.get("diagnostics", []))
                if call.get("artifact"):
                    report["outputs"].append(call["artifact"])
            statuses = [call.get("status") for call in report["calls"]]
            successful = {call["node"] for call in report["calls"] if call.get("status") == "succeeded"}
            all_observed = len(report["calls"]) == len(package.requirements["operations"]) and successful == set(package.requirements["operations"])
            report["execution"]["status"] = "unknown" if "unknown" in statuses else "succeeded" if result.returncode == 0 and all_observed else "failed"
            if report["execution"]["status"] == "succeeded":
                try:
                    report["workflowOutputs"] = _verify_engine_outputs(package, result.stdout, report["calls"])
                except Problem as exc:
                    report["execution"]["status"] = "failed"
                    report["diagnostics"].append(exc.diagnostic)
            if report["execution"]["status"] == "failed" and not report["diagnostics"]:
                report["diagnostics"].append({"code": "ENGINE_EXECUTION_FAILED", "category": "execution-failed", "requirement": "OUT-003", "message": "Engine did not produce exactly one successful call per declared node", "expected": sorted(package.requirements["operations"]), "observed": sorted(successful), "cause": {"exitCode": result.returncode}})
        except Problem as exc:
            report["diagnostics"].append(exc.diagnostic)
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            report["execution"]["status"] = "failed"
            report["diagnostics"].append({"code": "RUN_FAILURE", "category": "execution-failed", "requirement": "OUT-001", "message": "Execution could not complete", "cause": str(exc)})
            if isinstance(exc, subprocess.TimeoutExpired):
                (output / "engine-stdout.log").write_bytes(exc.stdout or b"")
                (output / "engine-stderr.log").write_bytes(exc.stderr or b"")
        # Retain completed call evidence even if the engine could not finish.
        # This also applies to a timeout or failure before collecting stdout.
        known_calls = {jsonio.encode(call) for call in report["calls"]}
        for path in sorted((output / "calls").glob("*.json")):
            call = jsonio.read(path)
            if jsonio.encode(call) not in known_calls:
                report["calls"].append(call)
                report["diagnostics"].extend(call.get("diagnostics", []))
                if call.get("artifact"):
                    report["outputs"].append(call["artifact"])
        if any(call.get("status") == "unknown" for call in report["calls"]):
            report["execution"]["status"] = "unknown"
        report["acceptance"] = acceptance.evaluate(package.requirements, report["calls"], output)
        jsonio.validate(report, jsonio.load_schema("run"), code="REPORT_INVALID", requirement="OUT-001")
        jsonio.write(output / "report.json", report)
        return report
