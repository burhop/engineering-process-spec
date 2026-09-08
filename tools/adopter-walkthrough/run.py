"""Prepare an isolated consumer and verify the documented installed interfaces.

No Wright checkout, source tree or Docker socket is mounted. Installation may
download public npm dependencies; the verification container has no network.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("wheel", "node-package", "example", "provider", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--image", default="eps-workflow-baseline:20260907")
    parser.add_argument("--record", type=Path, help="Explicit destination for the compact verified evidence JSON")
    args = parser.parse_args()
    output = args.out.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("--out must be a new or empty directory; previous evidence is never deleted")
    source = args.example.resolve()
    if output.is_relative_to(source):
        parser.error("--out must be outside the source package")
    if source.is_symlink() or any(p.is_symlink() for p in source.rglob("*")):
        parser.error("Example must contain ordinary files/directories, not symlinks")
    output.mkdir(parents=True, exist_ok=True)
    consumer = output / "consumer"
    consumer.mkdir()
    wheel = consumer / args.wheel.name
    tarball = consumer / args.node_package.name
    shutil.copyfile(args.wheel, wheel)
    shutil.copyfile(args.node_package, tarball)
    shutil.copyfile(args.provider, consumer / "mock_mcp_server.py")
    shutil.copytree(source, consumer / "package")
    scripts = Path(__file__).resolve().parent
    shutil.copyfile(scripts / "consumer.py", consumer / "consumer.py")
    node_project = consumer / "node-consumer"
    node_project.mkdir()
    shutil.copyfile(scripts / "integration.mjs", node_project / "integration.mjs")
    (node_project / "package.json").write_text('{"name":"epx-walkthrough-consumer","private":true,"type":"module"}\n', encoding="utf-8")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        parser.error("npm must be installed on the preparation host")
    setup = [npm, "install", str(tarball), "--ignore-scripts", "--no-audit", "--no-fund",
             "--prefix", str(node_project), "--cache", str(output / "npm-cache")]
    with (output / "npm-install.log").open("w", encoding="utf-8") as log:
        subprocess.run(setup, stdout=log, stderr=subprocess.STDOUT, check=True)
    node_lock = node_project / "package-lock.json"
    node_versions = {name: value["version"] for name, value in json.loads(node_lock.read_text(encoding="utf-8"))["packages"].items()
                     if name.startswith("node_modules/") and "version" in value}
    image = json.loads(subprocess.check_output(["docker", "image", "inspect", args.image], text=True))[0]
    prepared = {
        "wheelFilename": wheel.name, "nodeFilename": tarball.name,
        "wheelSha256": sha(wheel), "nodePackageSha256": sha(tarball),
        "providerSha256": sha(consumer / "mock_mcp_server.py"),
        "nodeConsumerLockSha256": sha(node_lock), "nodeDependencyVersions": node_versions,
        "packageMetadataSha256": sha(consumer / "package/ro-crate-metadata.json"),
        "image": {"name": args.image, "id": image["Id"], "os": image["Os"], "architecture": image["Architecture"]},
        "harnessSha256": {name: sha(scripts / name) for name in ("run.py", "consumer.py", "integration.mjs")},
    }
    (consumer / "prepared.json").write_text(json.dumps(prepared, indent=2) + "\n", encoding="utf-8")
    command = ["docker", "run", "--rm", "--network", "none", "--name", "epx-adopter-" + uuid.uuid4().hex[:12],
               "--mount", f"type=bind,source={consumer},target=/consumer", "--workdir", "/consumer", args.image,
               "python", "consumer.py"]
    with (output / "container.log").open("w", encoding="utf-8") as log:
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    if completed.returncode:
        print((output / "container.log").read_text(encoding="utf-8"), file=sys.stderr)
        return completed.returncode
    evidence = json.loads((consumer / "evidence.json").read_text(encoding="utf-8"))
    evidence["reproduce"] = "python tools/adopter-walkthrough/run.py --wheel WHEEL --node-package TGZ --example CALCULATION_DIRECTORY --provider MOCK_SERVER --out NEW_DIRECTORY"
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
