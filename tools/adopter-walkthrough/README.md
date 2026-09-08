# Isolated adopter walkthrough

This maintained check installs the local wheel and npm package into a fresh
consumer and executes the public calculation example without mounting this
repository or Wright into the verification container. It tests real MCP stdio
calls, existing cwltool/StreamFlow execution, installed API use, preserved bytes,
missing bindings and explicit replacement. It does not test actual CAD.

Prerequisites: Python 3.12+, npm and Docker with Linux containers on the
preparation host. The
[baseline image](../../experiments/workflow-baseline/README.md) provides Python
3.12.14, Node 24.13.1, cwltool 3.2.20260720092025 and StreamFlow 0.2.0rc2 from
pinned base-image digests and a dependency lock. Build local distribution
artifacts first; no registry publication is required:

```sh
python -m pip wheel --no-deps . --wheel-dir dist
npm ci --prefix applications/node --ignore-scripts
npm pack ./applications/node --pack-destination dist
docker build --tag eps-workflow-baseline:20260907 experiments/workflow-baseline
```

Run from the repository root, using a new output directory:

```sh
python tools/adopter-walkthrough/run.py --wheel dist/engineering_process_kit-0.1.0.dev1-py3-none-any.whl --node-package dist/epx-node-adopter-0.1.0-draft.1.tgz --example examples/calculation --provider tests/providers/mock_mcp_server.py --out artifacts/local/adopter-run
```

All source arguments can instead point to explicitly supplied artifacts outside
this repository. The script copies only the selected wheel, tarball, complete
calculation package, mock-provider source and this small harness into a new
consumer. It never imports Wright or receiver source modules from the checkout.
`--image` can select the already-built baseline image by tag or local image ID;
its actual image identity/platform and installed runtime versions are recorded.

Preparation installs the tarball with `npm install --ignore-scripts`, confining
the cache and dependencies to the requested output directory. Network access may
be required during preparation. The subsequent container uses `--network none`,
mounts only `OUT/consumer` at `/consumer`, and receives neither the Docker socket
nor a Wright path. Its wheel install is `--no-index --no-deps` because the pinned
engine image already supplies the declared runtime dependencies.

The fixture launcher is copied byte-for-byte and checked against the unchanged
package's identity pin. No test substitutes a different mock when that fails.
The later replacement intentionally creates revision `2`, retains the original
graph and source package, selects the explicitly named alternate mock application
and reruns acceptance. Both old/new cross-bindings must be rejected first.

The check returns nonzero if a command, preservation assertion, provider identity
or expected run outcome fails. Output contains exact command argv/exit codes,
stdout/stderr files, run reports, provider audit events and a fingerprinted
installed-source inventory. `OUT/consumer/evidence.json` is the compact index.
The detailed observed results remain available for diagnosing a failure; nothing
is deleted or rerun automatically against an existing nonempty output directory.

For a deliberate documentation-evidence refresh, append
`--record docs/adopter-evidence.json`. That writes evidence only after the entire
walkthrough passes. Retain the full local output when investigating failures.
The CI interface is this same command and its process exit status, followed by
inspection of the evidence's declared scope; a missing evidence file is not a
pass. The [full conformance cases](../../conformance/cases.json) remain a
separate gate.

Consumer sequence:

1. Install the wheel; use its bundled schemas and public reader API.
2. Validate, inspect and preserve the copied process with each receiver.
3. Configure the exact copied mock; confirm preflight makes zero engineering
   calls, then execute two named calls through each existing engine.
4. Use the installed Node package's public ESM API from a separate tiny app.
5. Reject missing bindings without changing source bytes.
6. Use both public `replace` commands, reject mismatched old/new bindings, then
   execute the deliberately replaced application with renewed acceptance.

The harness records execution/acceptance/approval separately. Passing this
walkthrough establishes the stated mock consumer path, not complete upstream
CWL conformance, real Solid Edge interoperability or outside adoption.
