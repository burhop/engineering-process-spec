"""Preserving package reader and semantic validation; no provider calls."""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import zipfile

from . import PROFILE, VERSION
from .errors import Problem, invalid
from . import jsonio

FEATURES = {"cwl-mcp-core", "quantity-acceptance", "resource-revisions"}
EXTENSION = "epx:ExchangeRequirement"
CWL_REQUIREMENTS = {"InlineJavascriptRequirement", "StepInputExpressionRequirement", "MultipleInputFeatureRequirement", EXTENSION}
CRATE_CONTEXT = "https://w3id.org/ro/crate/1.2/context"
PROCESS_FIELDS = {"id", "class", "label", "doc", "inputs", "outputs", "requirements", "hints", "cwlVersion", "$namespaces", "$schemas", "$base", "intent"}


def cwl_fields(value, allowed, location):
    if not isinstance(value, dict):
        raise invalid("CWL_SHAPE", "CWL-001", "CWL declaration must be an object", pointer=location)
    unknown = [key for key in value if key not in allowed and ":" not in key]
    if unknown:
        raise invalid("CWL_FIELD", "CWL-001", "Unknown unqualified CWL fields", pointer=location, observed=unknown)
    if "$base" in value:
        raise _unsupported("CWL base-URI overrides need another declared profile", pointer=location)
    if "cwlVersion" in value and value["cwlVersion"] != "v1.2":
        raise _unsupported("Only CWL v1.2 is implemented", pointer=location, observed=value["cwlVersion"])


def local_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise invalid("PACKAGE_PATH", "PKG-001", "Expected a package-relative slash-separated path", observed=relative)
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or relative.endswith("/"):
        raise invalid("PACKAGE_PATH", "PKG-001", "Path escapes or does not identify a package file", observed=relative)
    result = root.joinpath(*path.parts)
    if not result.resolve().is_relative_to(root.resolve()) or result.is_symlink():
        raise invalid("PACKAGE_PATH", "PKG-001", "Symlinks or escaping paths are not supported", observed=relative)
    return result


@contextmanager
def open_root(source: str | Path):
    """Extract only validated ZIP members; never alter the received archive."""
    source = Path(source).resolve()
    if source.is_dir():
        yield source
        return
    if not source.is_file() or not zipfile.is_zipfile(source):
        raise invalid("PACKAGE_UNREADABLE", "PKG-001", "Expected a package directory or ZIP", path=str(source))
    with tempfile.TemporaryDirectory(prefix="epx-package-") as temp:
        root = Path(temp)
        with zipfile.ZipFile(source) as archive:
            names = set()
            members = []
            for member in archive.infolist():
                if member.filename in names:
                    raise invalid("PACKAGE_DUPLICATE_MEMBER", "PKG-001", "Duplicate ZIP member", observed=member.filename)
                names.add(member.filename)
                if stat.S_ISLNK(member.external_attr >> 16):
                    raise invalid("PACKAGE_PATH", "PKG-001", "ZIP symlinks are unsupported", observed=member.filename)
                relative = member.filename.rstrip("/") if member.is_dir() else member.filename
                target = local_path(root, relative)
                members.append((member, target))
            for member, target in members:
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(member))
        yield root


@dataclass
class Package:
    root: Path
    metadata: dict
    requirements: dict
    workflow: dict
    main: dict
    inventory: dict[str, str]
    metadata_sha256: str
    workflow_path: str

    def payload(self, path: str) -> Path:
        if path not in self.inventory:
            raise invalid("PAYLOAD_NOT_INVENTORIED", "PKG-002", "Required payload lacks an inventory digest", path=path)
        return local_path(self.root, path)

    def execution_document(self):
        document = deepcopy(self.workflow)
        main = next(node for node in document["$graph"] if node.get("id") == "#main")
        del main["requirements"][EXTENSION]
        return document

    def summary(self):
        return {
            "status": "valid", "profile": self.requirements["profile"],
            "process": self.requirements["process"],
            "packageMetadataSha256": self.metadata_sha256,
            "nodes": self.requirements["operations"],
            "dependencies": self.requirements["bindings"],
            "resources": self.requirements["resources"],
            "payloads": self.inventory, "diagnostics": [],
            "availability": "not-checked", "engineeringCalls": 0,
        }


def _unsupported(message, **evidence):
    return Problem("FEATURE_UNSUPPORTED", "unsupported", "PKG-003", message, **evidence)


def load(root: Path) -> Package:
    try:
        return _load(root)
    except (AttributeError, TypeError, KeyError, IndexError) as exc:
        raise invalid("PACKAGE_SHAPE", "PKG-003", "Required package structure has an invalid shape", cause=str(exc)) from exc


def _load(root: Path) -> Package:
    root = root.resolve()
    metadata_path = root / "ro-crate-metadata.json"
    metadata = jsonio.read(metadata_path)
    if not isinstance(metadata, dict) or metadata.get("@context") != CRATE_CONTEXT or not isinstance(metadata.get("@graph"), list):
        raise invalid("CRATE_INVALID", "PKG-002", "Expected the declared RO-Crate 1.2 profile")
    graph = metadata["@graph"]
    try:
        ids = [entity["@id"] for entity in graph]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate entity IDs")
        entities = {entity["@id"]: entity for entity in graph}
        dataset = entities["./"]
        descriptor = entities["ro-crate-metadata.json"]
        if dataset["@type"] != "Dataset" or descriptor.get("@type") != "CreativeWork" or descriptor["about"] != {"@id": "./"}:
            raise ValueError("Dataset/metadata relationship")
        if any(not isinstance(dataset.get(key), str) or not dataset[key].strip() for key in ("name", "description", "datePublished")):
            raise ValueError("Root requires name, description and datePublished")
        published = dataset["datePublished"]
        if len(published) != 10 or date.fromisoformat(published).isoformat() != published:
            raise ValueError("Core datePublished uses YYYY-MM-DD")
        licensing = dataset.get("license")
        if isinstance(licensing, dict):
            license_entity = entities[licensing["@id"]]
            if any(not isinstance(license_entity.get(key), str) or not license_entity[key].strip() for key in ("name", "description")):
                raise ValueError("Referenced license needs name and description")
        elif not isinstance(licensing, str) or not licensing.strip():
            raise ValueError("Root requires a licensing statement or described license reference")
        workflow_path = dataset["mainEntity"]["@id"]
        conformances = dataset["conformsTo"]
        if isinstance(conformances, dict):
            conformances = [conformances]
        profile_ids = [item["@id"] for item in conformances]
    except (KeyError, TypeError, ValueError) as exc:
        raise invalid("CRATE_INVALID", "PKG-002", "Invalid root/metadata/entrypoint relationships", cause=str(exc)) from exc
    if PROFILE not in profile_ids:
        raise _unsupported("Package requires an unsupported profile", observed=profile_ids, expected=PROFILE)
    inventory = {}
    for relative, entity in entities.items():
        if entity.get("@type") != "File":
            continue
        if relative == "ro-crate-metadata.json":
            continue
        path = local_path(root, relative)
        expected = entity.get("sha256")
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            raise invalid("PAYLOAD_DIGEST_MISSING", "PKG-002", "File requires lowercase SHA-256", path=relative)
        if not path.is_file():
            raise invalid("PAYLOAD_MISSING", "PKG-002", "Packaged payload is missing", path=relative)
        observed = jsonio.digest(path.read_bytes())
        if expected != observed:
            raise invalid("PAYLOAD_DIGEST_MISMATCH", "PKG-002", "Packaged payload changed", path=relative, expected=expected, observed=observed)
        inventory[relative] = expected
    has_part = dataset.get("hasPart", [])
    if not isinstance(has_part, list) or {x.get("@id") for x in has_part if isinstance(x, dict)} != set(inventory):
        raise invalid("CRATE_PARTS", "PKG-002", "Dataset hasPart must identify each inventoried payload")
    if "requirements.json" not in inventory or workflow_path not in inventory:
        raise invalid("PAYLOAD_NOT_INVENTORIED", "PKG-002", "Requirements and entrypoint must be inventoried")
    requirements = jsonio.read(root / "requirements.json")
    jsonio.validate(requirements, jsonio.load_schema("requirements"))
    if requirements["profile"] != PROFILE or requirements["version"] != VERSION:
        raise _unsupported("Requirements version/profile is unsupported", expected=PROFILE, observed=requirements["profile"])
    unknown = set(requirements["requiredFeatures"]) - FEATURES
    if unknown:
        raise _unsupported("Required features are unsupported", observed=sorted(unknown))
    if not FEATURES.issubset(requirements["requiredFeatures"]):
        raise invalid("CORE_FEATURES_MISSING", "CORE-001", "The core requires all declared feature groups", expected=sorted(FEATURES))
    if requirements["process"]["entrypoint"] != workflow_path + "#main":
        raise invalid("ENTRYPOINT_MISMATCH", "CORE-002", "Metadata and requirements identify different entrypoints")
    if Path(workflow_path).suffix.lower() in {".yaml", ".yml"}:
        raise _unsupported("This core exchanges packed JSON CWL; YAML needs another declared profile")
    workflow = jsonio.read(local_path(root, workflow_path))
    cwl_fields(workflow, {"$graph", "$namespaces", "$schemas", "$base", "id", "cwlVersion"}, "/")
    if workflow.get("cwlVersion") != "v1.2":
        raise _unsupported("Only CWL v1.2 is implemented", observed=workflow.get("cwlVersion"))
    nodes = workflow.get("$graph")
    if not isinstance(nodes, list) or len({x.get("id") for x in nodes}) != len(nodes):
        raise invalid("CWL_GRAPH_INVALID", "CWL-001", "Expected a packed CWL graph with unique IDs")
    mains = [node for node in nodes if node.get("id") == "#main" and node.get("class") == "Workflow"]
    if len(mains) != 1:
        raise invalid("CWL_MAIN_INVALID", "CORE-002", "One #main Workflow is required")
    main = mains[0]
    if any(node.get("class") != "CommandLineTool" and node is not main for node in nodes):
        raise _unsupported("Additional workflows and other process classes are outside this fixed-call core")
    cwl_fields(main, PROCESS_FIELDS | {"steps"}, "/$graph/#main")
    cwl_requirements = main.get("requirements", {})
    if not isinstance(cwl_requirements, dict):
        raise _unsupported("This profile uses the CWL requirements map representation")
    if set(cwl_requirements) - CWL_REQUIREMENTS:
        raise _unsupported("Unknown required CWL features", observed=sorted(set(cwl_requirements) - CWL_REQUIREMENTS))
    namespaces = workflow.get("$namespaces", {}) | main.get("$namespaces", {})
    if namespaces.get("epx") != "urn:engineering-process-spec:profile:" or cwl_requirements.get(EXTENSION) != {"manifest": "requirements.json"}:
        raise invalid("EXCHANGE_REQUIREMENT", "CWL-002", "The mandatory exchange requirement/namespace is missing or different")
    steps = main.get("steps", {})
    if not isinstance(steps, dict) or not steps:
        raise invalid("CWL_STEPS_INVALID", "CWL-001", "Expected named CWL steps")
    operations = requirements["operations"]
    if {"main/" + key for key in steps} != set(operations):
        raise invalid("NODE_MAPPING", "CWL-003", "Every step must have exactly one operation requirement")
    tools = {node.get("id"): node for node in nodes if node.get("class") == "CommandLineTool"}
    dependencies = {}
    workflow_inputs = main.get("inputs", {})
    if "epx_context" not in workflow_inputs:
        raise invalid("CONTEXT_INPUT", "CWL-004", "The reserved local-context input is missing")
    for name, step in steps.items():
        node_id = "main/" + name
        cwl_fields(step, {"id", "label", "doc", "in", "out", "run", "requirements", "hints", "scatter", "scatterMethod", "when"}, "/steps/" + name)
        if any(key in step for key in ("scatter", "scatterMethod", "when")):
            raise _unsupported("Conditional/scattered steps require another declared execution profile", node=node_id)
        if step.get("requirements"):
            raise _unsupported("Step-local execution requirements require another declared profile", node=node_id)
        operation = operations[node_id]
        if operation["binding"] not in requirements["bindings"]:
            raise invalid("BINDING_REFERENCE", "BIND-001", "Operation refers to an undeclared binding", node=node_id)
        if step.get("run") not in tools:
            raise _unsupported("Step implementation is not a supported packed CommandLineTool", node=node_id)
        tool = tools[step["run"]]
        cwl_fields(tool, PROCESS_FIELDS | {"baseCommand", "arguments", "stdin", "stderr", "stdout", "successCodes", "temporaryFailCodes", "permanentFailCodes"}, "/$graph/" + step["run"])
        if any(key in tool for key in ("stdin", "stderr", "stdout", "successCodes", "temporaryFailCodes", "permanentFailCodes")):
            raise _unsupported("Adapter stream/exit-code overrides require another declared profile", node=node_id)
        if tool.get("baseCommand") not in ("epx-mcp-call", ["epx-mcp-call"]):
            raise _unsupported("The core currently executes fixed MCP command adapters", node=node_id)
        if tool.get("arguments") or tool.get("requirements") or tool.get("hints"):
            raise _unsupported("Additional command arguments/tool requirements need another declared adapter profile", node=node_id)
        signature = {"context": ("File", "--context"), "node": ("string", "--node"), "binding": ("string", "--binding"), "tool": ("string", "--tool"), "arguments_json": ("string", "--arguments-json")}
        if set(tool.get("inputs", {})) != set(signature):
            raise invalid("ADAPTER_SIGNATURE", "CWL-003", "Adapter input signature differs", node=node_id)
        for name_, (type_, prefix) in signature.items():
            parameter = tool["inputs"][name_]
            if parameter.get("type") != type_ or parameter.get("inputBinding", {}).get("prefix") != prefix or "valueFrom" in parameter.get("inputBinding", {}):
                raise invalid("ADAPTER_SIGNATURE", "CWL-003", "Adapter type/prefix/value mapping differs", node=node_id, dependency=name_)
        result_port = tool.get("outputs", {}).get("result", {})
        if result_port.get("type") != "File" or result_port.get("outputBinding", {}).get("glob") != "result.json":
            raise invalid("ADAPTER_OUTPUT", "CWL-005", "Adapter must expose its observed result.json File", node=node_id)
        incoming = step.get("in", {})
        if not isinstance(incoming, dict):
            raise _unsupported("This profile uses named CWL step-input mappings", node=node_id)
        if incoming.get("context") not in ("epx_context", {"source": "epx_context"}):
            raise invalid("CONTEXT_MAPPING", "CWL-004", "The receiving context must be passed unchanged to every adapter", node=node_id)
        expected = {"node": node_id, "binding": operation["binding"], "tool": operation["tool"]}
        for input_name, value in expected.items():
            if incoming.get(input_name) != {"default": value}:
                raise invalid("INVOCATION_MAPPING", "CWL-003", "Fixed node/binding/tool input differs from requirements", node=node_id, dependency=input_name, expected=value)
        contract_path = operation["toolContract"]
        if contract_path not in inventory:
            raise invalid("CONTRACT_MISSING", "BIND-004", "Tool snapshot is not inventoried", path=contract_path)
        contract = jsonio.read(local_path(root, contract_path))
        if contract.get("name") != operation["tool"] or not isinstance(contract.get("inputSchema"), dict) or not isinstance(contract.get("outputSchema"), dict):
            raise invalid("CONTRACT_INVALID", "BIND-004", "Tool snapshot lacks the declared name/input/output schema", node=node_id)
        parents = set()
        for value in incoming.values():
            sources = value.get("source", []) if isinstance(value, dict) else value
            if isinstance(sources, str):
                sources = [sources]
            for source in sources or []:
                if "/" in source:
                    parent, port = source.split("/", 1)
                    if parent not in steps or port not in steps[parent].get("out", []):
                        raise invalid("DATA_REFERENCE", "CWL-005", "Upstream output reference does not resolve", node=node_id, observed=source)
                    parents.add(parent)
                elif source not in workflow_inputs:
                    raise invalid("DATA_REFERENCE", "CWL-005", "Workflow input reference does not resolve", node=node_id, observed=source)
        dependencies[name] = parents
    workflow_outputs = main.get("outputs", {})
    if not isinstance(workflow_outputs, dict) or not workflow_outputs:
        raise invalid("WORKFLOW_OUTPUT", "CWL-005", "Declared workflow File outputs are required")
    for output_id, output in workflow_outputs.items():
        source = output.get("outputSource")
        if output.get("type") != "File" or not isinstance(source, str) or source.count("/") != 1:
            raise _unsupported("Core workflow outputs use one explicit File outputSource", dependency=output_id)
        parent, port = source.split("/")
        if parent not in steps or port not in steps[parent].get("out", []):
            raise invalid("OUTPUT_REFERENCE", "CWL-005", "Workflow output reference does not resolve", dependency=output_id, observed=source)
    pending = dict(dependencies)
    finished = set()
    while pending:
        ready = [key for key, parents in pending.items() if parents <= finished]
        if not ready:
            raise invalid("DATA_CYCLE", "CWL-001", "CWL data dependencies contain a cycle")
        for key in ready:
            finished.add(key)
            del pending[key]
    if requirements["job"] not in inventory:
        raise invalid("JOB_MISSING", "PKG-003", "Default job is not inventoried")
    default_job = jsonio.read(local_path(root, requirements["job"]))
    if not isinstance(default_job, dict) or "epx_context" in default_job:
        raise invalid("CONTEXT_INPUT", "CWL-004", "Portable input job must be an object without receiving execution context")
    from .inputs import validate_job
    validate_job(main, default_job)
    for resource_id, resource in requirements["resources"].items():
        if resource["binding"] not in requirements["bindings"]:
            raise invalid("RESOURCE_BINDING", "RES-001", "Resource binding does not resolve", dependency=resource_id)
    criterion_ids = set()
    for criterion in requirements["acceptance"]:
        from .acceptance import UNITS
        if criterion["unit"] not in UNITS:
            raise _unsupported("Acceptance unit is outside the explicit conversion table", dependency=criterion["id"], observed=criterion["unit"])
        if UNITS[criterion["unit"]][0] != criterion["quantity"]:
            raise invalid("ACCEPTANCE_DIMENSION", "ACC-001", "Acceptance quantity and unit dimensions differ", dependency=criterion["id"], expected=criterion["quantity"], observed=UNITS[criterion["unit"]][0])
        if criterion["id"] in criterion_ids or criterion["node"] not in operations:
            raise invalid("ACCEPTANCE_REFERENCE", "ACC-001", "Acceptance identifier is duplicated or node does not resolve")
        criterion_ids.add(criterion["id"])
        if "minimum" in criterion and criterion["minimum"] > criterion["maximum"]:
            raise invalid("ACCEPTANCE_BOUNDS", "ACC-001", "Acceptance minimum exceeds maximum")
    return Package(root, metadata, requirements, workflow, main, inventory, jsonio.digest(metadata_path.read_bytes()), workflow_path)


def preserve(source: str | Path, destination: str | Path):
    """Copy even unsupported definitions; reject overwrite and unsafe members."""
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(source):
        raise invalid("COPY_DESTINATION", "PKG-004", "Choose a new destination outside the source")
    if source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    else:
        for path in source.rglob("*"):
            if path.is_symlink():
                raise invalid("PACKAGE_PATH", "PKG-001", "Refusing to follow symlink while copying", path=str(path))
        shutil.copytree(source, destination)
    return {"status": "preserved", "source": str(source), "destination": str(destination), "engineeringCalls": 0}
