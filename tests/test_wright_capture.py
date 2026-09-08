"""External capture tests use temporary synthetic files, never a Wright runtime."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("wright_capture", Path(__file__).parents[1] / "tools" / "wright_capture.py")
CAPTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAPTURE)


class WrightCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "original.wflow"
        # Deliberately unparsed and not claimed valid .wflow; includes unfamiliar bytes.
        self.original = b"author-specific Solid Edge block\r\nopaque future field: \xff\x00\r\n"
        self.source.write_bytes(self.original)

    def test_preserves_source_exactly_and_reports_missing_facts(self):
        out = self.root / "capture"
        report = CAPTURE.capture(self.source, out)
        self.assertEqual((out / "original.workflow.wflow").read_bytes(), self.original)
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertFalse(report["sourceParsed"])
        self.assertFalse(report["conformingExport"])
        self.assertFalse(report["executable"])
        self.assertEqual(report["engineeringCalls"], 0)
        self.assertIn("canonical-context-unavailable", [gap["code"] for gap in report["missingOrUnverifiedFacts"]])
        self.assertEqual(report["observedFiles"][0]["sha256"], CAPTURE.digest(self.original))

    def test_rejects_wright_output_and_existing_output_without_changes(self):
        protected = self.root / "wright"
        protected.mkdir()
        with self.assertRaises(CAPTURE.CaptureError):
            CAPTURE.capture(self.source, protected / "capture", wright_roots=(protected,))
        self.assertFalse((protected / "capture").exists())
        with self.assertRaises(CAPTURE.CaptureError):
            CAPTURE.capture(self.source, Path("D:/repos/wright/.local-run/forbidden-capture"))
        existing = self.root / "existing"
        existing.mkdir()
        sentinel = existing / "keep.txt"
        sentinel.write_text("original")
        with self.assertRaises(CAPTURE.CaptureError):
            CAPTURE.capture(self.source, existing)
        self.assertEqual(sentinel.read_text(), "original")
        self.assertEqual(list(existing.iterdir()), [sentinel])

    def test_companion_digests_are_assertions_and_never_trigger_implicit_reads(self):
        canonical = self.root / "canonical.json"
        canonical.write_text(json.dumps({"document_kind": "workflow-ir", "schema_version": "2.0.0-recovery.1", "workflow_id": "workflow.example", "revision": 3, "blocks": []}))
        facts = self.root / "facts.json"
        facts.write_text(json.dumps({"format": "epx-wright-binding-facts", "version": CAPTURE.VERSION,
                                    "sourceSha256": CAPTURE.digest(self.original), "canonicalSha256": CAPTURE.digest(canonical.read_bytes()),
                                    "bindings": {"local-server": {"implementation": {"id": "https://github.com/burhop/SolidEdgeMCP"},
                                                                  "application": {"id": "solid_edge"},
                                                                  "toolContracts": [{"file": "not-present-and-must-not-be-read.json"}], "resources": []}}}))
        report = CAPTURE.capture(self.source, self.root / "capture", canonical=canonical, binding_facts=facts)
        self.assertTrue(report["canonicalInspection"]["recognizedContract"])
        self.assertFalse(report["canonicalInspection"]["schemaValidated"])
        self.assertEqual(report["canonicalInspection"]["sourceAssociation"], "author-asserted-match")
        self.assertEqual(report["implicitFilesRead"], 0)
        self.assertEqual(report["suppliedBindings"][0]["evidenceStatus"], "supplied-unverified")
        self.assertIn("application.version", report["suppliedBindings"][0]["missingIdentityFields"])
        self.assertFalse(report["conformingExport"])
        self.assertEqual((self.root / "capture" / "canonical.original.json").read_bytes(), canonical.read_bytes())
        self.assertEqual((self.root / "capture" / "binding-facts.original.json").read_bytes(), facts.read_bytes())

    def test_malformed_optional_json_is_preserved_and_not_interpreted(self):
        canonical = self.root / "bad.json"
        canonical.write_bytes(b'{"duplicate":1,"duplicate":2}')
        report = CAPTURE.capture(self.source, self.root / "capture", canonical=canonical)
        self.assertEqual(report["canonicalInspection"]["status"], "invalid-json-preserved")
        self.assertFalse(report["canonicalInspection"]["recognizedContract"])
        self.assertEqual((self.root / "capture" / "canonical.original.json").read_bytes(), canonical.read_bytes())

    def test_missing_explicit_input_refuses_before_creating_output(self):
        out = self.root / "capture"
        with self.assertRaises(FileNotFoundError):
            CAPTURE.capture(self.source, out, canonical=self.root / "missing.json")
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
