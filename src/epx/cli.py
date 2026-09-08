"""Public consumer CLI. Inspection and validation never contact providers."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import VERSION
from . import jsonio, mcp
from .errors import Problem
from .package import load, open_root, preserve


def demo_bindings(provider, output):
    provider = Path(provider).resolve()
    binding = {
        "format": "epx-bindings", "version": VERSION,
        "bindings": {"engineering": {
            "implementation": {"id": "urn:engineering-process-spec:mock-mcp", "revision": VERSION},
            "application": {"id": "urn:engineering-process-spec:mock-engineering", "version": VERSION},
            "transport": {"kind": "stdio", "command": sys.executable, "arguments": ["-u", str(provider)]},
            "trust": {"kind": "launcher-sha256", "path": str(provider), "sha256": jsonio.digest(provider.read_bytes())},
        }},
    }
    jsonio.write(Path(output), binding)
    return {"status": "configured", "path": str(Path(output).resolve()), "scope": "explicit mock fixture only"}


def parser():
    result = argparse.ArgumentParser(description="Experimental engineering-process exchange kit")
    result.add_argument("--version", action="version", version=VERSION)
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("inspect", "validate"):
        command = commands.add_parser(name)
        command.add_argument("package")
    command = commands.add_parser("preflight")
    command.add_argument("package")
    command.add_argument("--bindings", required=True)
    command = commands.add_parser("run")
    command.add_argument("package")
    command.add_argument("--bindings", required=True)
    command.add_argument("--engine", choices=["cwltool", "streamflow"], default="cwltool")
    command.add_argument("--out", required=True)
    command.add_argument("--job")
    command = commands.add_parser("preserve")
    command.add_argument("package")
    command.add_argument("destination")
    command = commands.add_parser("replace")
    command.add_argument("package")
    command.add_argument("--binding", required=True)
    command.add_argument("--with", dest="replacement", required=True)
    command.add_argument("--revision", required=True)
    command.add_argument("--out", required=True)
    command = commands.add_parser("demo-bindings")
    command.add_argument("--provider", required=True)
    command.add_argument("--out", required=True)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    exit_code = 0
    try:
        if args.command == "demo-bindings":
            result = demo_bindings(args.provider, args.out)
        elif args.command == "preserve":
            result = preserve(args.package, args.destination)
        elif args.command == "replace":
            from .replacement import replace
            result = replace(args.package, args.binding, jsonio.read(Path(args.replacement)), args.revision, args.out)
        elif args.command == "run":
            from .runner import run
            result = run(args.package, args.bindings, args.out, args.engine, args.job)
            if result["execution"]["status"] != "succeeded" or result["acceptance"]["status"] != "pass":
                exit_code = 3
        else:
            with open_root(args.package) as root:
                package = load(root)
                if args.command == "preflight":
                    result = mcp.preflight(package, mcp.configuration(Path(args.bindings)))
                else:
                    result = package.summary()
        sys.stdout.write(jsonio.encode(result).decode("utf-8"))
    except Problem as exc:
        category = exc.diagnostic["category"]
        result = {"status": category, "diagnostics": [exc.diagnostic], "engineeringCalls": 0}
        sys.stdout.write(jsonio.encode(result).decode("utf-8"))
        exit_code = 1 if category == "invalid" else 2
    except (OSError, ValueError, TypeError, KeyError) as exc:
        sys.stdout.write(jsonio.encode({"status": "invalid", "diagnostics": [{"code": "INPUT_ERROR", "category": "invalid", "requirement": "PKG-001", "message": str(exc)}]}).decode())
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
