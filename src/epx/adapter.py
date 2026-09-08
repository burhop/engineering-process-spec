"""CWL task program; graph execution remains the existing CWL engine's job."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import uuid

from . import IMPLEMENTATION, VERSION
from . import jsonio, mcp
from .errors import Problem, invalid, unavailable
from .package import load


def call(context_path, node, binding, tool, arguments_json):
    context = jsonio.read(Path(context_path))
    run_directory = Path(context["runDirectory"]).resolve()
    record = {
        "format": "epx-call", "version": VERSION, "runId": context["runId"],
        "implementation": IMPLEMENTATION, "node": node, "binding": binding,
        "tool": tool, "effect": "read-only", "status": "blocked", "diagnostics": [],
        "packageMetadataSha256": context["packageMetadataSha256"],
        "inputSha256": jsonio.digest(arguments_json.encode("utf-8")),
        "request": {"method": "tools/call", "params": {"name": tool}},
    }
    phase = "preflight"
    client = None
    try:
        if context.get("format") != "epx-run-context" or context.get("version") != VERSION:
            raise invalid("CONTEXT_INVALID", "CWL-004", "Unknown local execution context")
        package = load(Path(context["package"]))
        if package.metadata_sha256 != context["packageMetadataSha256"]:
            raise invalid("PACKAGE_CHANGED", "PKG-002", "Package changed after execution preparation")
        operation = package.requirements["operations"].get(node)
        if operation is None or operation["binding"] != binding or operation["tool"] != tool:
            raise invalid("INVOCATION_MAPPING", "CWL-003", "Adapter invocation differs from authoritative operation", node=node)
        record["effect"] = operation["effect"]
        arguments = jsonio.loads(arguments_json)
        record["request"]["params"]["arguments"] = arguments
        descriptor = jsonio.read(package.payload(operation["toolContract"]))
        jsonio.validate(arguments, descriptor["inputSchema"], code="ARGUMENTS_INVALID", requirement="BIND-004")
        config = mcp.configuration(Path(context["bindings"]))
        required = package.requirements["bindings"][binding]
        record["intendedProvider"] = required
        local = config["bindings"].get(binding)
        if local is None:
            raise unavailable("PROVIDER_UNAVAILABLE", "BIND-005", "No local connection for intended binding", dependency=binding)
        mcp.verify_local(required, local, binding)
        with mcp.Client(local) as client:
            observed, resources = mcp.verify_session(package, config, binding, client)
            record["observedProvider"], record["resources"] = observed, resources
            phase = "call"
            result = client.request("tools/call", record["request"]["params"])
            record["result"] = result
            if not isinstance(result, dict):
                raise Problem("TOOL_RESULT_INVALID", "execution-failed", "OUT-003", "Tool result is not an object", node=node)
            if result.get("isError") is True:
                raise Problem("TOOL_ERROR", "execution-failed", "OUT-003", "MCP tool reported isError", node=node, cause=result)
            if "structuredContent" not in result:
                raise Problem("TOOL_RESULT_INVALID", "execution-failed", "OUT-003", "Required structured tool output is absent", node=node)
            try:
                jsonio.validate(result["structuredContent"], descriptor["outputSchema"], code="TOOL_RESULT_INVALID", requirement="BIND-004")
            except Problem as exc:
                exc.diagnostic["category"] = "execution-failed"
                exc.diagnostic["node"] = node
                raise
            phase = "persist"
            data = jsonio.encode(result)
            digest = jsonio.digest(data)
            relative = "artifacts/" + node.replace("/", "-") + "/" + digest + ".json"
            artifact = run_directory / relative
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_bytes(data)
            Path("result.json").write_bytes(data)
            record["resultSha256"] = digest
            record["artifact"] = {"path": relative, "sha256": digest, "durability": "persistent", "mediaType": "application/json"}
            record["status"] = "succeeded"
    except mcp.LostResponse as exc:
        unknown = phase == "call" and record["effect"] == "mutation" and client is not None and client.last_call_sent
        category = "outcome-unknown" if unknown else ("unavailable" if phase == "preflight" else "execution-failed")
        record["status"] = "unknown" if unknown else ("blocked" if phase == "preflight" else "failed")
        record["diagnostics"].append({"code": "MUTATION_OUTCOME_UNKNOWN" if unknown else "MCP_CONNECTION_FAILED", "category": category, "requirement": "RES-003", "message": str(exc), "node": node})
    except mcp.RpcFailure as exc:
        record["status"] = "blocked" if phase == "preflight" else "failed"
        record["diagnostics"].append({"code": "MCP_RPC_ERROR", "category": "unavailable" if phase == "preflight" else "execution-failed", "requirement": "OUT-003", "message": "MCP protocol request failed", "cause": exc.error, "node": node})
    except Problem as exc:
        record["status"] = "failed" if exc.diagnostic["category"] == "execution-failed" else "blocked"
        record["diagnostics"].append(exc.diagnostic)
    except (ValueError, TypeError, OSError, KeyError) as exc:
        record["status"] = "failed" if phase != "preflight" else "blocked"
        record["diagnostics"].append({"code": "ADAPTER_FAILURE", "category": "execution-failed" if phase != "preflight" else "invalid", "requirement": "OUT-001", "message": "Adapter cannot complete the operation", "cause": str(exc), "node": node})
    record_path = run_directory / "calls" / (node.replace("/", "-") + "-" + str(uuid.uuid4()) + ".json")
    jsonio.write(record_path, record)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description="Execute one author-bound MCP operation; not a workflow interpreter")
    for name in ("context", "node", "binding", "tool", "arguments-json"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args(argv)
    try:
        record = call(args.context, args.node, args.binding, args.tool, args.arguments_json)
    except (Problem, OSError, ValueError, KeyError) as exc:
        diagnostic = exc.diagnostic if isinstance(exc, Problem) else {"message": str(exc)}
        sys.stderr.write(jsonio.encode(diagnostic).decode())
        return 1
    if record["status"] != "succeeded":
        sys.stderr.write(jsonio.encode(record["diagnostics"]).decode())
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
