"""Retain one complete conformance run as a reviewable report and evidence ZIP."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Completed run directory")
    parser.add_argument("--out", type=Path, required=True, help="New or empty retained result directory")
    options = parser.parse_args()
    source, output = options.source.resolve(), options.out.resolve()
    if output == source or output.is_relative_to(source):
        parser.error("Retained output must be separate from the source run")
    if output.exists() and any(output.iterdir()):
        parser.error("Retained output must be new or empty; prior evidence is never overwritten")
    report = json.loads((source / "report.json").read_text(encoding="utf-8"))
    if not report.get("completedAt"):
        parser.error("The report has not completed")
    output.mkdir(parents=True, exist_ok=True)
    files = {}
    archive = output / "evidence.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                parser.error("Evidence export does not follow symbolic links: " + str(path))
            if path.is_file() and path != source / "report.json":
                relative = path.relative_to(source).as_posix()
                payload = path.read_bytes()
                files[relative] = hashlib.sha256(payload).hexdigest()
                stream.writestr(relative, payload)
        stream.writestr("evidence-manifest.json", json.dumps(files, indent=2) + "\n")
    report["retention"] = {
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "sourceReportSha256": hashlib.sha256((source / "report.json").read_bytes()).hexdigest(),
        "archive": "evidence.zip", "archiveSha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "fileCount": len(files),
        "evidencePaths": "Case evidenceDirectory paths resolve inside the archive. Extract beside this report to inspect the original directory layout.",
        "excluded": ["Top-level report.json is retained separately; all other source files are included."],
    }
    (output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"report": str(output / "report.json"), "retention": report["retention"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
