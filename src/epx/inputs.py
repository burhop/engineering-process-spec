"""Check a supplied input job against its existing CWL input declarations.

This validates data shapes, not expressions or provider availability. CWL remains
the authority for types/defaults; the workflow engine supplies default values.
"""

import math

from .errors import Problem, invalid


def finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def nullable(kind):
    return kind == "null" or isinstance(kind, str) and kind.endswith("?") or isinstance(kind, list) and any(nullable(item) for item in kind)


def check_value(value, kind, pointer):
    if isinstance(kind, list):
        problems = []
        for variant in kind:
            try:
                check_value(value, variant, pointer)
                return
            except Problem as problem:
                problems.append(problem)
        if any(item.diagnostic["category"] == "unsupported" for item in problems):
            raise next(item for item in problems if item.diagnostic["category"] == "unsupported")
        raise invalid("CWL_INPUT_TYPE", "CWL-001", "Input does not match any declared union member", pointer=pointer, expected=kind)
    if isinstance(kind, dict):
        if kind.get("type") == "record":
            if not isinstance(value, dict):
                raise invalid("CWL_INPUT_TYPE", "CWL-001", "Input must be a record", pointer=pointer)
            fields = kind.get("fields", [])
            if isinstance(fields, dict):
                fields = [{"name": name, **(field if isinstance(field, dict) else {"type": field})} for name, field in fields.items()]
            if not isinstance(fields, list):
                raise invalid("CWL_INPUT_TYPE", "CWL-001", "Record fields must be a list or map", pointer=pointer)
            for field in fields:
                name = field["name"].split("/")[-1].split("#")[-1]
                field_pointer = pointer + "/" + name
                if name not in value:
                    if "default" in field:
                        check_value(field["default"], field["type"], field_pointer)
                    elif not nullable(field["type"]):
                        raise invalid("CWL_INPUT_REQUIRED", "CWL-001", "Required record field is absent", pointer=field_pointer, expected=field["type"])
                else:
                    check_value(value[name], field["type"], field_pointer)
            return
        if kind.get("type") == "enum":
            if value not in kind.get("symbols", []):
                raise invalid("CWL_INPUT_TYPE", "CWL-001", "Input is not a declared enumeration symbol", pointer=pointer)
            return
        if kind.get("type") == "array":
            if not isinstance(value, list):
                raise invalid("CWL_INPUT_TYPE", "CWL-001", "Input must be an array", pointer=pointer)
            for index, item in enumerate(value):
                check_value(item, kind["items"], pointer + "/" + str(index))
            return
        return check_value(value, kind.get("type"), pointer)
    if isinstance(kind, str) and kind.endswith("?"):
        return check_value(value, ["null", kind[:-1]], pointer)
    if isinstance(kind, str) and kind.endswith("[]"):
        return check_value(value, {"type": "array", "items": kind[:-2]}, pointer)
    predicates = {
        "null": lambda: value is None,
        "boolean": lambda: isinstance(value, bool),
        "string": lambda: isinstance(value, str),
        "int": lambda: isinstance(value, int) and not isinstance(value, bool) and -(2**31) <= value < 2**31,
        "long": lambda: isinstance(value, int) and not isinstance(value, bool) and -(2**63) <= value < 2**63,
        "float": lambda: finite_number(value),
        "double": lambda: finite_number(value),
        "File": lambda: isinstance(value, dict) and value.get("class") == "File",
        "Directory": lambda: isinstance(value, dict) and value.get("class") == "Directory",
        "Any": lambda: value is not None,
    }
    if kind not in predicates:
        raise Problem("CWL_INPUT_TYPE_UNSUPPORTED", "unsupported", "CWL-001", "Input type needs an unsupported named schema or type", pointer=pointer, observed=kind)
    if not predicates[kind]():
        raise invalid("CWL_INPUT_TYPE", "CWL-001", "Input value does not have its declared CWL type", pointer=pointer, expected=kind)


def validate_job(main, job):
    if not isinstance(job, dict) or "epx_context" in job:
        raise invalid("CONTEXT_INPUT", "CWL-004", "Portable input jobs cannot supply receiving execution context")
    for name, declaration in main["inputs"].items():
        if name == "epx_context":
            continue
        parameter = declaration if isinstance(declaration, dict) else {"type": declaration}
        if name not in job or (job[name] is None and "default" in parameter):
            if "default" in parameter:
                check_value(parameter["default"], parameter["type"], "/inputs/" + name)
            elif not nullable(parameter["type"]):
                raise invalid("CWL_INPUT_REQUIRED", "CWL-001", "Required workflow input is absent", pointer="/inputs/" + name, expected=parameter["type"])
        else:
            check_value(job[name], parameter["type"], "/inputs/" + name)
