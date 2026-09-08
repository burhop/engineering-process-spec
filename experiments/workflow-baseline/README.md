# Existing-engine baseline experiment

Observed 2026-09-07. This is a bounded implementation experiment, not a claim of
profile or general CWL/MCP conformance. Nothing in Wright was executed or modified.

## Outcome

Use CWL v1.2 for the first profile experiment. The **same**
[two-step workflow](cwl-handoff.cwl) executed in cwltool
`3.2.20260720092025` and StreamFlow `0.2.0rc2`, with identical JSON receipts.
The first command produces a quantity with an explicitly mock provider identifier;
the second consumes its output file, checks its value/unit and writes a receipt.
The workflow has no hidden Python module or Wright dependency. Its small Python
commands are task programs, not workflow interpreters.

The OWS `1.0.3` candidate did not yield two native MCP execution paths:

| Probe | Observed result | Scope |
|---|---|---|
| Synapse native runner, set + expression handoff | Passed after installing its jq dependency | Runner actually built and executed |
| Same runner, `call: mcp`, protocol `2025-11-25` | Rejected: `Unknown/unsupported function 'mcp'` | Workflow task initialization failed before any MCP transport was created |
| Both OWS probe definitions | Valid under the official `v1.0.3` workflow schema | Structural validation only |
| Java SDK at `c481ddb4...` | Schema contains MCP, runtime handlers omit MCP | Source inspection only; no Java runtime execution claimed |
| CWL two-step file handoff, both engines | Passed, identical receipt bytes | Workflow scheduling, command invocation and file handoff; **no MCP call yet** |

Synapse returns process exit code **0 even for the observed MCP failure**. A test
that checks only the shell exit code would falsely pass. The reproducible probe
asserts the returned artifact and diagnostic. No MCP server was running at the
sample's loopback discard endpoint; rejection occurs before attempting it.

This result does not prove that OWS cannot support MCP. Both engines could gain
adapters, and other versions may differ. It does establish the additional work
at these exact revisions. CWL already supplies two usable execution engines;
the profile must now specify a fixed-call MCP CommandLineTool adapter contract
and test separately implemented adapters through **both** engines. The mock
identifier in this experiment is never a stand-in for Solid Edge.

## Reproduce the successful baseline

Prerequisite: Docker with Linux containers and permission to pull public images.
No CAD installation, credentials, model API or Wright services are needed. On
Windows, run from the repository root:

```powershell
./experiments/workflow-baseline/run-baseline.ps1
```

Equivalent commands after resolving the experiment directory to an absolute path:

```powershell
docker build --tag eps-workflow-baseline:20260907 experiments/workflow-baseline
docker run --rm --network none --name eps-workflow-baseline-probe --mount type=bind,source=D:/repos/engineering-process-spec/experiments/workflow-baseline,target=/work eps-workflow-baseline:20260907 sh run-cwl.sh
```

The container has no host Docker socket, no Wright directory and no network
access during execution. On Linux/macOS, pass the corresponding absolute local
directory in `source=`. Linux/amd64 containers on this Windows host were tested;
native Windows engine execution and other container architectures were not.

Expected stdout contains `equalReceipt: true`, `accepted: true`, value `2.5`,
unit `mm` and provider `urn:engineering-process:experiment:mock`. The script also
asserts equality. Results and fresh engine logs are under `.work/`:

- `cwltool-result.json` and `streamflow-result.json`: each engine's CWL output
  object, including the output File's location, size and engine checksum.
- `cwltool-output/receipt.json` and `streamflow-output/receipt.json`: identical
  task-generated JSON payloads. Engine metadata need not match because each run
  has different output locations.
- `cwltool.log`, `streamflow.log`, version files and `python-lock.txt`.

The exact engine entrypoints in [run-cwl.sh](run-cwl.sh) avoid ambiguity from two
packages registering `cwl-runner`:

```sh
python -m cwltool --no-container --outdir .work/cwltool-output cwl-handoff.cwl
python -c 'from streamflow.cwl.runner import run; run()' --outdir .work/streamflow-output cwl-handoff.cwl
```

Node `24.13.1` is additionally included for the later independent JavaScript MCP
adapter. It is not used by this baseline's task programs. This image includes
the Node binary and license notice; it does not include npm.

## Reproduce the OWS rejection

The optional [probe-ows.ps1](probe-ows.ps1) downloads the pinned Synapse source
and jq `1.8.1` into ignored `.work/`, restores NuGet dependencies there, builds
the native runner and checks the control and rejection. It needs Windows x64,
.NET SDK capable of targeting `net9.0`, the .NET 9 runtime, and public network
access for installation. The recorded build used SDK `10.0.301` and succeeded
with zero errors and warnings. Upstream direct package versions are pinned in
its project files; the complete transitive NuGet graph is not locked here.

```powershell
./experiments/workflow-baseline/probe-ows.ps1
```

The source archive retains its upstream license files and source headers. The
downloaded jq binary is checked against its official SHA-256 checksum. A first
control run found jq missing; supplying this declared runtime dependency made
the control succeed. That installation failure is distinct from native MCP
support being absent.

## Version and independence evidence

[observations.json](observations.json) records pins, observed statuses and input/
output digests. [requirements.lock.txt](requirements.lock.txt) pins the complete
resolved Python environment. The [Dockerfile](Dockerfile) pins base image
digests; its Docker image ID is specific to the recorded build, not an upstream
release identifier. [cwltool-observed.log](cwltool-observed.log) and
[streamflow-observed.log](streamflow-observed.log) retain actual execution logs.

StreamFlow `0.2.0rc2` was installed from its released wheel, not its moving
`master`. The wheel's source files were scanned: no Python `import cwltool` or
`from cwltool` statements were found. Its `streamflow/cwl/translator.py`,
`streamflow/cwl/command.py` and workflow/connector layers construct execution
steps, command lines and local process/file transfers. The recorded logs show
that path actually ran. Its release [project metadata](https://github.com/alpha-unito/streamflow/blob/7704a8e705abbd6338b6f049a60165b39a1f5e72/pyproject.toml)
and [command implementation](https://github.com/alpha-unito/streamflow/blob/7704a8e705abbd6338b6f049a60165b39a1f5e72/streamflow/cwl/command.py)
are authoritative source references.

The two engines share Python, `cwl-utils` (including generated CWL parsing and
expression utilities), schema-salad and other lower-level packages. This is
independent workflow execution, not independent parsing or independent
organizational adoption. Adapter independence is outside this baseline probe.

## Upstream sources and notices

- [OWS schema `v1.0.3`](https://github.com/open-workflow-specification/specification/blob/v1.0.3/schema/workflow.yaml).
  Downloaded schema SHA-256 is recorded; both sample definitions were checked
  with `jsonschema.Draft202012Validator` after loading YAML.
- [Synapse task factory](https://github.com/serverlessworkflow/synapse/blob/ba3fbfd5125995bba9fb5900aed181a0775d538c/src/runner/Synapse.Runner/Services/TaskExecutorFactory.cs)
  and [function executor](https://github.com/serverlessworkflow/synapse/blob/ba3fbfd5125995bba9fb5900aed181a0775d538c/src/runner/Synapse.Runner/Services/Executors/FunctionCallExecutor.cs).
  Synapse's Apache-2.0 notices remain in the downloaded source and restored
  packages; no modified Synapse code is part of this repository.
- [Java runtime factory](https://github.com/open-workflow-specification/sdk-java/blob/c481ddb4d42dc068343542ebeaa158d399b694b4/impl/core/src/main/java/io/serverlessworkflow/impl/executors/DefaultTaskExecutorFactory.java)
  and [runtime modules](https://github.com/open-workflow-specification/sdk-java/blob/c481ddb4d42dc068343542ebeaa158d399b694b4/impl/README.md).
  The schema is newer than the handler set. No Java execution is claimed.
- [cwltool release metadata](https://pypi.org/project/cwltool/3.2.20260720092025/)
  and [StreamFlow release metadata](https://pypi.org/project/streamflow/0.2.0rc2/).
  Dependencies remain installed with their `.dist-info` metadata and upstream
  notices: cwltool Apache-2.0, StreamFlow LGPL-3.0-or-later, and each dependency's
  own terms. Upstream packages are not vendored as this project's source.
- [jq `1.8.1` checksums](https://github.com/jqlang/jq/releases/download/jq-1.8.1/sha256sum.txt),
  [Node `v24.13.1` license](https://github.com/nodejs/node/blob/v24.13.1/LICENSE)
  and [Python `v3.12.14` license](https://github.com/python/cpython/blob/v3.12.14/LICENSE).
  The image retains the Python distribution's notices and explicitly copies
  Node's license to `/usr/local/share/doc/node/LICENSE`.

These are dependency notices, not a choice of this repository's license or
authorization for publication. Legal and public-distribution gates stay open.
