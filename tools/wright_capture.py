"""Preserve explicitly supplied Wright material and report capture gaps; never convert or execute it."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


VERSION = "0.1.0-draft.1"
MAPPING = "wright-080-20260907.1"
PROFILE = f"urn:engineering-process-spec:core:{VERSION}"
MAX_BYTES = 16 * 1024 * 1024


class CaptureError(ValueError):
    """A refused capture; no existing input/output material may be overwritten."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def strict_json(data: bytes) -> Any:
    def constant(_: str) -> None:
        raise ValueError("Non-finite JSON numeric literal")

    value = json.loads(data.decode("utf-8"), object_pairs_hook=strict_pairs, parse_constant=constant)

    def finite(item: Any) -> bool:
        if isinstance(item, float):
            return math.isfinite(item)
        if isinstance(item, dict):
            return all(finite(child) for child in item.values())
        if isinstance(item, list):
            return all(finite(child) for child in item)
        return True

    if not finite(value):
        raise ValueError("Non-finite JSON value")
    return value


def read_input(path: Path, role: str) -> dict:
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise CaptureError(f"{role} must identify one explicit ordinary file")
    if resolved.stat().st_size > MAX_BYTES:
        raise CaptureError(f"{role} exceeds the capture tool's 16 MiB input limit")
    data = resolved.read_bytes()
    return {"role": role, "originalPath": str(resolved), "sha256": digest(data), "sizeBytes": len(data), "data": data}


def protected_output(output: Path, additional_roots: tuple[Path, ...]) -> bool:
    # The Windows checkout remains forbidden even when this utility is tested on Linux.
    lexical = str(output).replace("\\", "/").rstrip("/").casefold()
    default = "d:/repos/wright"
    if lexical == default or lexical.startswith(default + "/"):
        return True
    resolved = output.resolve()
    roots = [Path("D:/repos/wright").resolve(), *(root.resolve() for root in additional_roots)]
    return any(resolved == root or resolved.is_relative_to(root) for root in roots)


def companion(record: dict | None) -> tuple[Any, str]:
    if record is None:
        return None, "not-supplied"
    try:
        return strict_json(record["data"]), "parsed-json-only"
    except (UnicodeError, ValueError, RecursionError):
        return None, "invalid-json-preserved"


def fact_gaps(facts: Any) -> tuple[list[dict], list[dict]]:
    gaps: list[dict] = []
    supplied: list[dict] = []
    if not isinstance(facts, dict) or facts.get("format") != "epx-wright-binding-facts" or facts.get("version") != VERSION:
        return [{"code": "binding-facts-not-understood", "field": "bindingFacts", "message": "Supply the documented optional binding-fact format; original bytes remain preserved."}], []
    bindings = facts.get("bindings")
    if not isinstance(bindings, dict) or not bindings:
        return [{"code": "binding-facts-missing", "field": "bindings", "message": "No explicit intended provider mappings were supplied."}], []
    for local_id, binding in bindings.items():
        if not isinstance(binding, dict):
            gaps.append({"code": "binding-facts-incomplete", "field": f"bindings/{local_id}", "message": "Binding facts must be an object."})
            continue
        fields = {
            "implementation.id": binding.get("implementation", {}).get("id") if isinstance(binding.get("implementation"), dict) else None,
            "implementation.revision": binding.get("implementation", {}).get("revision") if isinstance(binding.get("implementation"), dict) else None,
            "application.id": binding.get("application", {}).get("id") if isinstance(binding.get("application"), dict) else None,
            "application.version": binding.get("application", {}).get("version") if isinstance(binding.get("application"), dict) else None,
            "protocolVersion": binding.get("protocolVersion"),
        }
        missing = [name for name, value in fields.items() if not isinstance(value, str) or not value.strip()]
        for name in missing:
            gaps.append({"code": "binding-facts-incomplete", "field": f"bindings/{local_id}/{name}", "message": "Required identity/version fact has not been supplied; no value was inferred."})
        for name in ("toolContracts", "resources"):
            if not isinstance(binding.get(name), list) or not binding[name]:
                gaps.append({"code": "binding-evidence-missing", "field": f"bindings/{local_id}/{name}", "message": "Supply explicit contract/resource evidence before considering an executable export."})
        supplied.append({"localServerId": local_id, "identityFields": fields, "missingIdentityFields": missing,
                         "toolContractReferences": binding.get("toolContracts", []), "resourceReferences": binding.get("resources", []),
                         "evidenceStatus": "supplied-unverified", "referencedFilesRead": False})
    return gaps, supplied


def capture(source: Path, output: Path, *, canonical: Path | None = None,
            binding_facts: Path | None = None, wright_roots: tuple[Path, ...] = ()) -> dict:
    """Read only explicit inputs; output is a new preservation folder, never a core package."""
    if protected_output(output, wright_roots):
        raise CaptureError("Output must be outside the read-only Wright checkout and its resolved aliases")
    if output.exists() or output.is_symlink():
        raise CaptureError("Output already exists; select a new capture directory")
    original = read_input(source, "original-wflow")
    canonical_record = read_input(canonical, "canonical-json") if canonical else None
    fact_record = read_input(binding_facts, "binding-facts") if binding_facts else None
    canonical_value, canonical_status = companion(canonical_record)
    facts, facts_status = companion(fact_record)
    recognized = isinstance(canonical_value, dict) and canonical_value.get("document_kind") == "workflow-ir" and canonical_value.get("schema_version") == "2.0.0-recovery.1"
    gaps: list[dict] = []
    if not recognized:
        gaps.append({"code": "canonical-context-unavailable", "field": "canonical", "message": "The observed recovery canonical context was not supplied as recognized JSON; no accepted base is inferred."})
    association = "not-supplied"
    if isinstance(facts, dict) and facts.get("sourceSha256"):
        association = "author-asserted-match" if facts["sourceSha256"] == original["sha256"] else "mismatch"
        if canonical_record is not None:
            association = "author-asserted-match" if association == "author-asserted-match" and facts.get("canonicalSha256") == canonical_record["sha256"] else "mismatch"
    if association != "author-asserted-match":
        gaps.append({"code": "source-association-unverified", "field": "sourceSha256/canonicalSha256", "message": "No matching explicit source/canonical digest association was supplied."})
    binding_gaps, supplied = fact_gaps(facts)
    gaps.extend(binding_gaps)
    gaps.extend([
        {"code": "provider-evidence-not-verified", "field": "bindings", "message": "Supplied identities and referenced contracts/resources are assertions; this offline capture did not contact providers or read implicit files."},
        {"code": "execution-variant-not-authored", "field": "CWL", "message": "No explicit supported CWL variant or verified semantic mapping was supplied or generated."},
    ])
    canonical_inspection = {"status": canonical_status, "recognizedContract": recognized, "schemaValidated": False,
                            "sourceAssociation": association}
    if isinstance(canonical_value, dict):
        canonical_inspection.update({"documentKind": canonical_value.get("document_kind"), "schemaVersion": canonical_value.get("schema_version"),
                                     "workflowId": canonical_value.get("workflow_id"), "revision": canonical_value.get("revision")})
        for name in ("blocks", "ports", "relationships", "bindings", "components"):
            canonical_inspection[name + "Count"] = len(canonical_value[name]) if isinstance(canonical_value.get(name), list) else None
    records = [original, *([canonical_record] if canonical_record else []), *([fact_record] if fact_record else [])]
    targets = {"original-wflow": "original.workflow.wflow", "canonical-json": "canonical.original.json", "binding-facts": "binding-facts.original.json"}
    observations = [{**{key: value for key, value in record.items() if key != "data"}, "preservedPath": targets[record["role"]]} for record in records]
    report = {"format": "epx-wright-capture", "version": VERSION, "mappingRevision": MAPPING,
              "targetProfile": PROFILE, "observedAt": datetime.now(timezone.utc).isoformat(),
              "status": "preserved-not-converted", "conformingExport": False, "executable": False,
              "sourceParsed": False, "engineeringCalls": 0, "implicitFilesRead": 0, "observedFiles": observations,
              "canonicalInspection": canonical_inspection, "bindingFactsStatus": facts_status,
              "suppliedBindings": supplied, "missingOrUnverifiedFacts": gaps,
              "preservedUnsupportedSemantics": [
                  {"scope": "complete-original-source", "status": "opaque-preserved", "reason": "No .wflow parser or Wright runtime is imported; no block or language interpretation is claimed."},
                  {"scope": "AI tasks, approval/rework, adapter/resource semantics when present", "status": "not-converted", "reason": "Capture does not infer a fixed-call sequence or human approval from source text or supplied context."}],
              "nextAction": "Review supplied and missing facts, verify intended provider/contracts/resources, then explicitly author or implement a separately tested CWL mapping. Keep this capture as original-source provenance."}
    destination = output.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    for record in records:
        with (destination / targets[record["role"]]).open("xb") as stream:
            stream.write(record["data"])
    with (destination / "capture-report.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Explicit original .wflow file; preserved as opaque bytes")
    parser.add_argument("--out", required=True, type=Path, help="New capture directory outside Wright")
    parser.add_argument("--canonical", type=Path, help="Explicit optional original canonical JSON file")
    parser.add_argument("--binding-facts", type=Path, help="Explicit optional binding-fact JSON file")
    parser.add_argument("--wright-root", action="append", type=Path, default=[], help="Additional read-only checkout/mount roots; never replaces the default protected D:/repos/wright")
    options = parser.parse_args()
    try:
        report = capture(options.source, options.out, canonical=options.canonical, binding_facts=options.binding_facts, wright_roots=tuple(options.wright_root))
    except (CaptureError, OSError) as error:
        print(json.dumps({"status": "refused", "message": str(error), "conformingExport": False}), file=sys.stderr)
        return 2
    print(json.dumps({"status": report["status"], "conformingExport": False, "executable": False, "report": str(options.out / "capture-report.json"), "gaps": len(report["missingOrUnverifiedFacts"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
