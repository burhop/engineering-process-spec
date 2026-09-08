"""Exact-byte identities and JSON operations, with no network schema resolution."""

from __future__ import annotations

import hashlib
from importlib import resources
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry
from referencing.exceptions import NoSuchResource

from .errors import invalid


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reject_constant(value: str):
    raise ValueError(f"Non-finite JSON number: {value}")


def loads(data: str | bytes):
    def object_members(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON member: {key}")
            result[key] = item
        return result
    value = json.loads(data, parse_constant=reject_constant, object_pairs_hook=object_members)
    ensure_finite(value)
    return value


def ensure_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Non-finite JSON number")
    if isinstance(value, dict):
        for item in value.values():
            ensure_finite(item)
    if isinstance(value, list):
        for item in value:
            ensure_finite(item)


def read(path: Path):
    try:
        return loads(path.read_bytes())
    except (OSError, ValueError) as exc:
        raise invalid("JSON_INVALID", "PKG-001", "Cannot read a finite JSON document", path=str(path), cause=str(exc)) from exc


def encode(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode(value))


def load_schema(name: str):
    return loads(resources.files("epx.schemas").joinpath(name + ".schema.json").read_bytes())


def _no_network(uri):
    raise NoSuchResource(ref=uri)


def validate(value, schema: dict, *, code="SCHEMA_INVALID", requirement="PKG-003"):
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, registry=Registry(retrieve=_no_network))
        errors = list(validator.iter_errors(value))
    except Exception as exc:
        raise invalid(code, requirement, "Schema cannot be evaluated with available local resources", cause=str(exc)) from exc
    if errors:
        error = min(errors, key=lambda e: len(e.absolute_path))
        raise invalid(code, requirement, error.message, pointer="/" + "/".join(map(str, error.absolute_path)))


def pointer(value, path: str):
    if path == "":
        return value
    if not path.startswith("/"):
        raise ValueError("JSON Pointer must begin with /")
    for token in path[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def equal(left, right) -> bool:
    """JSON-value equality. Booleans do not compare equal to numbers."""
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(equal(a, b) for a, b in zip(left, right))
    return left == right
