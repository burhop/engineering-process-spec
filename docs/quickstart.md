# Run a process without Wright

This experimental draft runs a named mock MCP calculation through an existing
CWL engine. It needs no Wright service, paid CAD installation, credentials or
model-provider API. Expected output is volume `0.00002 m3`, mass `0.157 kg`,
execution `succeeded`, acceptance `pass` and approval `not-requested`.

## Prepare the tools

The tested executor environment is Linux/amd64, Python **3.12.14**, Node
**24.13.1**, cwltool **3.2.20260720092025** and StreamFlow **0.2.0rc2**. Windows
can run this environment with Docker Linux containers. Native Windows readers
were exercised; native Windows CWL execution is not a supported test claim.

From this repository, build the local wheel and the pinned engine image:

```sh
python -m pip wheel --no-deps . --wheel-dir dist
docker build --tag eps-workflow-baseline:20260907 experiments/workflow-baseline
```

The image contains the engines and Node; install the local wheel into it for
each fresh demonstration container. For native Linux, use a Python environment
and install the wheel plus
[requirements.lock.txt](../experiments/workflow-baseline/requirements.lock.txt),
and supply Node 24.13.1 on PATH. Installation may need network access; execution
of this example does not. Local build/install is supported; public publication
and this project's licensing terms remain later decisions.

## Receive a standalone example

Create a new consumer directory containing only these public artifacts:

```text
consumer/
  engineering_process_kit-0.1.0.dev1-py3-none-any.whl
  mock_mcp_server.py
  package/                       # copy of examples/calculation/
```

Copy the wheel from `dist/`, the explicit test provider from
`tests/providers/mock_mcp_server.py` and the **whole**
[calculation package](../examples/calculation/README.md). Do not change its
manifest pins or inventory. The provider's copied bytes must match its declared
SHA-256; the package contains no local endpoint or launch path.

Start a fresh container with only this directory mounted. Substitute its absolute
host path below; no repository or Wright mount is needed:

```sh
docker run --rm -it --network none --mount type=bind,source=/absolute/path/to/consumer,target=/consumer --workdir /consumer eps-workflow-baseline:20260907 sh
```

Inside it, run:

```sh
python -m pip install --no-deps /consumer/engineering_process_kit-0.1.0.dev1-py3-none-any.whl
epx validate package
epx inspect package
epx preserve package saved-package
epx demo-bindings --provider /consumer/mock_mcp_server.py --out /consumer/local-bindings.json
epx preflight package --bindings local-bindings.json
epx run package --bindings local-bindings.json --engine cwltool --out run-python
```

`validate` and `inspect` report the definition and perform no provider calls.
`preserve` copies bytes to a new destination, including unfamiliar content.
`demo-bindings` is explicitly for this mock: it records the receiver's launcher
path and verifies its bytes. `preflight` contacts the intended provider for
protocol, tool-contract and resource observations, with zero engineering calls.
`run` delegates the graph to cwltool and makes the declared MCP calls.

Read `run-python/report.json`: `execution.status` and `acceptance.status` are
separate. Its `calls` identify actual provider observations and result artifacts;
`artifacts/` retains those JSON bytes. Engine logs are diagnostic evidence, not
engineering acceptance. Keep `private/` and receiving configuration local; they
are not portable process inputs. Use a fresh output directory for every run.

For the missing-provider case, create this separate `missing-bindings.json`:

```json
{"format":"epx-bindings","version":"0.1.0-draft.1","bindings":{}}
```

```sh
epx preflight package --bindings missing-bindings.json
```

Expect `unavailable`, zero engineering calls and unchanged package bytes. A
valid definition remains meaningful when its intended provider is unavailable.

## Use the independent receiver

The [Node application](../applications/node/README.md) is a separately implemented
reader/binder/MCP adapter using StreamFlow. Its package includes the schemas; it
does not import the Python receiver. Build its local package from the repository:

```sh
npm ci --prefix applications/node --ignore-scripts
npm pack ./applications/node --pack-destination dist
```

In another consuming project, install the resulting local `.tgz` with
`npm install /absolute/path/to/epx-node-adopter-0.1.0-draft.1.tgz --ignore-scripts`.
With the same copied package, receiving bindings, Node and pinned StreamFlow:

```sh
epx-node inspect package
epx-node preflight package --bindings local-bindings.json
epx-node run package --bindings local-bindings.json --engine streamflow --out run-node
```

When locally installed npm binaries are not on PATH, use
`./node_modules/.bin/epx-node` instead. The expected quantities and identity
requirements match the Python path; implementation-specific output paths and
run IDs need not match.

## Verification scope

The copied-wheel walkthrough and installed Node CLI/public API were executed
with networking disabled and without a repository/Wright mount. Both paths
performed two real mock MCP calls with passing acceptance. The walkthrough also
verified byte preservation, zero engineering calls during preflight, bundled
schema use outside the checkout and the missing-binding diagnostic. This is
mock protocol/binding evidence, not a real Solid Edge run or independent
organizational adoption. Full mandatory-core claims come from the versioned
conformance reports, not this one happy path.

Continue with the [examples](../examples/README.md),
[authoring guide](authoring.md), [application integration guide](implementer-guide.md)
and [diagnostics](diagnostics.md). The [Solid Edge capture gate](wright-compatibility.md#real-solid-edge-capture-gate)
identifies what a real-provider fixture still needs.

The [maintained adopter walkthrough](../tools/adopter-walkthrough/README.md)
automates this copied-artifact check and the explicit replacement commands. Its
[recorded evidence](adopter-evidence.json) identifies exact distribution hashes,
installed-source fingerprints, runtime versions, commands and scope.
