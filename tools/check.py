"""Local/CI contract checks. Runtime conformance is a separate actual-engine run."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator
from epx.errors import Problem
from epx.package import load

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".work", ".cache", ".venv", "node_modules", "build", "dist", "__pycache__", ".tmp"}


def files(suffix):
    found = []
    for directory, children, filenames in os.walk(ROOT):
        children[:] = [name for name in children if name not in EXCLUDED and not name.endswith(".egg-info")]
        found.extend(Path(directory) / name for name in filenames if name.endswith(suffix))
    return found


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_report(path, requirements):
    report = read(path)
    assert report["coreConformanceDemonstrated"] is True, "Full core not demonstrated"
    assert report["sourcesStableDuringRun"] is True, "Sources changed during evidence run"
    catalog = read(ROOT / "conformance/cases.json")
    mandatory = {case["id"] for case in catalog["cases"] if case["mandatory"]}
    for implementation in ("python", "node"):
        outcomes = {case["id"]: case["status"] for case in report["cases"] if case["implementation"] == implementation}
        assert all(outcomes.get(identifier) == "passed" for identifier in mandatory), f"Missing/failing core case: {implementation}"
        coverage = report["requirementCoverage"][implementation]
        assert all(coverage.get(identifier, {}).get("status") == "passed" for identifier in requirements), f"Unproven required rule: {implementation}"
    for relative, expected in report["sourceSnapshotAfter"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, f"Stale conformance source: {relative}"
    retention = report.get("retention")
    if retention and retention.get("archive"):
        archive = retention["archive"] if isinstance(retention["archive"], dict) else {"path": retention["archive"], "sha256": retention["archiveSha256"]}
        archive_path = path.parent / archive["path"]
        assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == archive["sha256"], "Retained evidence archive digest differs"
        with zipfile.ZipFile(archive_path) as evidence:
            assert evidence.testzip() is None, "Retained evidence archive is corrupt"
    return {"path": str(path), "counts": report["counts"], "status": "passed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Also verify a retained full conformance report against current source")
    parser.add_argument("--out", type=Path, help="Write machine-readable check results")
    options = parser.parse_args()
    results = []
    def check(name, callback):
        try:
            detail = callback()
            results.append({"check": name, "status": "passed", "detail": detail})
        except Exception as error:
            results.append({"check": name, "status": "failed", "reason": str(error)})
    def schemas():
        paths = list((ROOT / "schemas").glob("*.schema.json"))
        for path in paths: Draft202012Validator.check_schema(read(path))
        return len(paths)
    check("canonical schemas", schemas)
    def examples():
        names = []
        for path in sorted((ROOT / "examples").iterdir()):
            if not (path / "ro-crate-metadata.json").exists(): continue
            try:
                load(path)
                assert path.name != "inspection-approval", "Required approval was silently ignored"
            except Problem as problem:
                assert path.name == "inspection-approval" and problem.diagnostic["category"] == "unsupported", problem.diagnostic
            names.append(path.name)
        return names
    check("example semantics and unsupported approval", examples)
    def command(argv):
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
        assert result.returncode == 0, (result.stdout + result.stderr)[-4000:]
        return {"argv": argv, "exitCode": result.returncode}
    check("deterministic fixture drift", lambda: command([sys.executable, "tools/build_examples.py", "--check"]))
    check("focused Python invariants", lambda: command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]))
    def links():
        broken = []
        count = 0
        for path in files(".md"):
            body = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
            for target in re.findall(r"\]\(([^)]+)\)", body):
                target = target.strip().split(' "', 1)[0].strip("<>")
                if not target or target.startswith("#") or urlsplit(target).scheme: continue
                filename = unquote(target.split("#", 1)[0])
                if not filename: continue
                count += 1
                resolved = (path.parent / filename).resolve()
                if not resolved.exists(): broken.append(f"{path.relative_to(ROOT)}: {target}")
        assert not broken, "Broken local document links: " + "; ".join(broken)
        return {"localTargetsChecked": count, "externalLinks": "not fetched", "anchors": "not checked"}
    check("local documentation targets", links)
    requirements = set(re.findall(r"\*\*([A-Z]+-\d{3})\s+—", (ROOT / "spec/core-draft.md").read_text(encoding="utf-8")))
    def mapping():
        cases = read(ROOT / "conformance/cases.json")["cases"]
        mapped = {requirement for case in cases if case["mandatory"] for requirement in case["requirements"]}
        assert not requirements - mapped, f"Unmapped requirements: {sorted(requirements - mapped)}"
        assert not mapped - requirements, f"Unknown requirement IDs: {sorted(mapped - requirements)}"
        assert len({case["id"] for case in cases}) == len(cases), "Duplicate case IDs"
        return {"requirements": len(requirements), "mandatoryCases": sum(case["mandatory"] for case in cases)}
    check("requirement-to-test mapping", mapping)
    if options.report: check("full conformance report integrity", lambda: check_report(options.report, requirements))
    report = {"format": "epx-repository-checks", "checks": results, "status": "passed" if all(item["status"] == "passed" for item in results) else "failed", "runtimeConformance": "see supplied report" if options.report else "not run by this command"}
    text = json.dumps(report, indent=2) + "\n"
    print(text)
    if options.out:
        options.out.parent.mkdir(parents=True, exist_ok=True)
        options.out.write_text(text, encoding="utf-8", newline="\n")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
