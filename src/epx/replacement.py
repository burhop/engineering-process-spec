"""Explicit, limited provider replacement; never an automatic fallback."""

from copy import deepcopy
from pathlib import Path

from . import VERSION, jsonio
from .errors import invalid
from .package import load, open_root, preserve


def replace(source, binding, replacement, revision, output):
    """Retain graph/contracts, revise one intended binding, expose review impact.

    This operation does not prove another application's engineering equivalence.
    The receiving environment must supply a new local binding and preflight it.
    """
    destination = Path(output).resolve()
    with open_root(source) as root:
        package = load(root)
        previous = package.requirements
        if binding not in previous["bindings"]:
            raise invalid("REPLACEMENT_BINDING", "BIND-006", "The named binding does not exist", dependency=binding)
        if not isinstance(revision, str) or not revision.strip() or revision == previous["process"]["revision"]:
            raise invalid("REPLACEMENT_REVISION", "BIND-006", "Explicit replacement requires a distinct nonempty process revision")
        updated = deepcopy(previous)
        updated["bindings"][binding] = deepcopy(replacement)
        updated["process"]["revision"] = revision
        jsonio.validate(updated, jsonio.load_schema("requirements"), requirement="BIND-006")
        if jsonio.equal(previous["bindings"][binding], replacement):
            raise invalid("REPLACEMENT_UNCHANGED", "BIND-006", "Replacement must change the intended binding; local connection changes do not revise a process")
        direct = {node for node, operation in previous["operations"].items() if operation["binding"] == binding}
        impacted = set(direct)
        changed = True
        while changed:
            changed = False
            for step_name, step in package.main["steps"].items():
                node = "main/" + step_name
                for parameter in step["in"].values():
                    sources = parameter.get("source", []) if isinstance(parameter, dict) else parameter
                    if isinstance(sources, str):
                        sources = [sources]
                    if node not in impacted and any("/" in item and "main/" + item.split("/")[0] in impacted for item in sources or []):
                        impacted.add(node)
                        changed = True
        original_bytes = (root / "requirements.json").read_bytes()
        original_digest = jsonio.digest(original_bytes)
        provenance_path = "provenance/requirements-" + original_digest + ".json"
        edit_path = "provenance/replacement-" + original_digest + ".json"
        if (root / edit_path).exists():
            raise invalid("REPLACEMENT_PROVENANCE", "BIND-006", "Replacement provenance target already exists")
        report = {
            "format": "epx-replacement", "version": VERSION,
            "processId": previous["process"]["id"], "previousRevision": previous["process"]["revision"],
            "revision": revision, "binding": binding,
            "previousRequirementsSha256": original_digest, "previousRequirements": provenance_path,
            "before": previous["bindings"][binding], "after": replacement,
            "directNodes": sorted(direct), "impactedNodes": sorted(impacted),
            "acceptanceRequiresRerun": [item["id"] for item in previous["acceptance"] if item["node"] in impacted],
            "approval": "not-requested", "historicalEvidence": "retained; never carried forward as new acceptance",
            "reviewRequired": ["tool input/output contracts", "resource identities and revisions", "data mappings and downstream acceptance"],
            "engineeringEquivalence": "not-established", "engineeringCalls": 0,
        }
        preserve(root, destination)
        (destination / provenance_path).parent.mkdir(parents=True, exist_ok=True)
        (destination / provenance_path).write_bytes(original_bytes)
        jsonio.write(destination / edit_path, report)
        jsonio.write(destination / "requirements.json", updated)
        metadata = deepcopy(package.metadata)
        dataset = next(item for item in metadata["@graph"] if item["@id"] == "./")
        for relative in ("requirements.json", provenance_path, edit_path):
            payload = (destination / relative).read_bytes()
            entity = next((item for item in metadata["@graph"] if item["@id"] == relative), None)
            if entity is None:
                entity = {"@id": relative, "@type": "File"}
                metadata["@graph"].append(entity)
                dataset["hasPart"].append({"@id": relative})
            entity.update(sha256=jsonio.digest(payload), contentSize=str(len(payload)))
        jsonio.write(destination / "ro-crate-metadata.json", metadata)
        load(destination)
        return {"status": "replaced", "destination": str(destination), **report}
