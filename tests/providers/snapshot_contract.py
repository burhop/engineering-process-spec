"""Check or explicitly regenerate this mock provider's reviewed contract snapshots."""

import argparse
import json
from pathlib import Path
import sys

from mock_mcp_server import TOOLS


def snapshots() -> dict[str, str]:
    expected = {}
    for tool in TOOLS:
        for suffix, value in (("tool", tool), ("input", tool["inputSchema"]), ("output", tool["outputSchema"])):
            expected[f"{tool['name']}.{suffix}.json"] = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    return expected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Explicitly replace snapshots after reviewing a contract change")
    options = parser.parse_args()
    root = Path(__file__).resolve().parent / "snapshots"
    if options.write:
        root.mkdir(exist_ok=True)
    mismatches = []
    for name, expected in snapshots().items():
        path = root / name
        if options.write:
            path.write_text(expected, encoding="utf-8", newline="\n")
        elif not path.exists() or path.read_bytes() != expected.encode("utf-8"):
            mismatches.append(name)
    if mismatches:
        print("Snapshot mismatch: " + ", ".join(mismatches), file=sys.stderr)
        return 1
    print(f"{'Wrote' if options.write else 'Verified'} {len(snapshots())} mock contract snapshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
