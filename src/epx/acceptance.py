"""Finite, dimension-checked quantities from observed, digest-verified results."""

from __future__ import annotations

import math
from pathlib import Path

from . import jsonio

# Explicit UCUM subset; no unit grammar or undeclared conversion guessing.
UNITS = {
    "m": ("length", 1.0), "mm": ("length", 0.001),
    "kg": ("mass", 1.0), "g": ("mass", 0.001),
    "m3": ("volume", 1.0), "mm3": ("volume", 1e-9),
    "kg/m3": ("density", 1.0), "g/cm3": ("density", 1000.0),
}


def evaluate(requirements, calls, run_directory: Path):
    criteria = []
    for criterion in requirements["acceptance"]:
        item = {"id": criterion["id"], "node": criterion["node"], "status": "not-run"}
        matches = [call for call in calls if call.get("node") == criterion["node"] and call.get("status") == "succeeded"]
        if not matches:
            item["reason"] = "No successful observed call for this criterion"
            criteria.append(item)
            continue
        if len(matches) != 1:
            item.update(status="indeterminate", reason="Ambiguous multiple successful calls for fixed node")
            criteria.append(item)
            continue
        call = matches[0]
        try:
            artifact = call["artifact"]
            path = (run_directory / artifact["path"]).resolve()
            if not path.is_relative_to(run_directory.resolve()):
                raise ValueError("Result artifact escapes run bundle")
            data = path.read_bytes()
            if jsonio.digest(data) != artifact["sha256"] or artifact["sha256"] != call["resultSha256"]:
                raise ValueError("Result artifact digest does not match observed call")
            result = jsonio.loads(data)
            if not jsonio.equal(result, call["result"]) or not call.get("observedProvider"):
                raise ValueError("Artifact is not tied to observed provider/call result")
            value = jsonio.pointer(result, criterion["valuePointer"])
            unit = jsonio.pointer(result, criterion["unitPointer"])
            quantity = jsonio.pointer(result, criterion["quantityPointer"])
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Quantity must have a finite numeric value")
            item.update(observed={"value": value, "unit": unit, "quantity": quantity}, artifactSha256=artifact["sha256"])
            if unit not in UNITS or criterion["unit"] not in UNITS:
                item.update(status="indeterminate", reason="Unit conversion is outside the declared subset")
            elif quantity != criterion["quantity"] or UNITS[unit][0] != criterion["quantity"] or UNITS[criterion["unit"]][0] != criterion["quantity"]:
                item.update(status="fail", reason="Quantity meaning or dimensions differ")
            else:
                factor = UNITS[unit][1] / UNITS[criterion["unit"]][1]
                normalized = value * factor
                if not math.isfinite(normalized):
                    raise ValueError("Converted quantity is outside the finite numeric range")
                item["normalized"] = {"value": normalized, "unit": criterion["unit"]}
                if "expected" in criterion:
                    passed = abs(normalized - criterion["expected"]) <= criterion["absoluteTolerance"]
                    item["expected"] = criterion["expected"]
                    item["absoluteTolerance"] = criterion["absoluteTolerance"]
                else:
                    passed = criterion["minimum"] <= normalized <= criterion["maximum"]
                    item.update(minimum=criterion["minimum"], maximum=criterion["maximum"])
                item["status"] = "pass" if passed else "fail"
        except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            item.update(status="indeterminate", reason=str(exc))
        criteria.append(item)
    statuses = {criterion["status"] for criterion in criteria}
    status = "fail" if "fail" in statuses else "indeterminate" if "indeterminate" in statuses or statuses == {"pass", "not-run"} else "not-run" if "not-run" in statuses else "pass"
    return {"status": status, "criteria": criteria}
