"""Focused invariants beyond the public black-box interoperability suite."""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from epx import acceptance, jsonio
from epx.errors import Problem
from epx.package import load
from epx.replacement import replace
from epx.runner import _verify_engine_outputs

ROOT = Path(__file__).resolve().parents[1]


class PythonInvariants(unittest.TestCase):
    def test_missing_and_mistyped_cwl_record_fields_are_invalid(self):
        from epx.inputs import validate_job
        package = load(ROOT / "examples/calculation")
        original = jsonio.read(package.root / "inputs/job.json")
        for change in ("missing", "type"):
            job = deepcopy(original)
            if change == "missing":
                del job["length"]["quantity"]
            else:
                job["length"]["value"] = "100"
            with self.subTest(change=change), self.assertRaises(Problem) as caught:
                validate_job(package.main, job)
            self.assertEqual(caught.exception.diagnostic["category"], "invalid")

    def test_conversion_avoids_intermediate_overflow_and_reports_unrepresentable_values(self):
        for quantity, unit, target, expected_status in (("density", "g/cm3", "g/cm3", "pass"), ("mass", "kg", "g", "indeterminate")):
            with self.subTest(quantity=quantity), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                result = {"structuredContent": {"quantity": quantity, "unit": unit, "value": 1e308}}
                data = jsonio.encode(result)
                digest = jsonio.digest(data)
                (root / "result.json").write_bytes(data)
                call = {"node": "main/measurement", "status": "succeeded", "observedProvider": {"implementation": "fixture"}, "artifact": {"path": "result.json", "sha256": digest}, "resultSha256": digest, "result": result}
                requirement = {"acceptance": [{"id": "measurement", "node": "main/measurement", "valuePointer": "/structuredContent/value", "unitPointer": "/structuredContent/unit", "quantityPointer": "/structuredContent/quantity", "quantity": quantity, "unit": target, "expected": 1e308, "absoluteTolerance": 0}]}
                outcome = acceptance.evaluate(requirement, [call], root)
                self.assertEqual(outcome["status"], expected_status)
                jsonio.encode(outcome)  # Neither an infinity nor a null masquerades as a quantity.

    def test_ambiguous_and_nonfinite_json_rejected(self):
        for data in ('{"id":1,"id":2}', '{"value":NaN}', '{"value":1e999}'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                jsonio.loads(data)

    def test_missing_engine_output_cannot_succeed_from_call_log(self):
        package = load(ROOT / "examples/calculation")
        with self.assertRaises(Problem):
            _verify_engine_outputs(package, b"{}", [{"node": "main/mass", "status": "succeeded"}])

    def test_explicit_replacement_preserves_source_graph_and_exposes_impact(self):
        source = ROOT / "examples/calculation"
        before = {p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()}
        binding = deepcopy(load(source).requirements["bindings"]["engineering"])
        binding["application"]["id"] = "urn:engineering-process-spec:mock-other-engineering"
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "revision-2"
            result = replace(source, "engineering", binding, "2", destination)
            self.assertEqual(result["impactedNodes"], ["main/mass", "main/volume"])
            self.assertEqual(len(result["acceptanceRequiresRerun"]), 2)
            self.assertEqual(result["engineeringCalls"], 0)
            self.assertEqual((destination / result["previousRequirements"]).read_bytes(), before[Path("requirements.json")])
            for path, data in before.items():
                self.assertEqual((source / path).read_bytes(), data)
                if path.name not in {"requirements.json", "ro-crate-metadata.json"}:
                    self.assertEqual((destination / path).read_bytes(), data)
            self.assertEqual(load(destination).requirements["process"]["revision"], "2")
            with self.assertRaises(Problem):
                replace(source, "engineering", binding, "1", Path(temporary) / "unchanged")
            self.assertFalse((Path(temporary) / "unchanged").exists())

    def test_acceptance_rejects_duplicate_or_tampered_observations(self):
        requirements = {"acceptance": [{"id": "mass", "node": "main/mass", "valuePointer": "/structuredContent/value", "unitPointer": "/structuredContent/unit", "quantityPointer": "/structuredContent/quantity", "quantity": "mass", "unit": "kg", "expected": 0.157, "absoluteTolerance": 0.000001}]}
        result = {"structuredContent": {"quantity": "mass", "unit": "kg", "value": 0.157}}
        data = jsonio.encode(result)
        digest = jsonio.digest(data)
        call = {"node": "main/mass", "status": "succeeded", "observedProvider": {"implementation": "fixture"}, "artifact": {"path": "result.json", "sha256": digest}, "resultSha256": digest, "result": result}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "result.json").write_bytes(data)
            self.assertEqual(acceptance.evaluate(requirements, [call], root)["status"], "pass")
            partial = deepcopy(requirements)
            partial["acceptance"].append({**partial["acceptance"][0], "id": "later", "node": "main/later"})
            self.assertEqual(acceptance.evaluate(partial, [call], root)["status"], "indeterminate")
            self.assertEqual(acceptance.evaluate(requirements, [call, call], root)["status"], "indeterminate")
            (root / "result.json").write_bytes(b"{}")
            self.assertEqual(acceptance.evaluate(requirements, [call], root)["status"], "indeterminate")


if __name__ == "__main__":
    unittest.main()
