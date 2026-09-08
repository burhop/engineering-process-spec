# Implement this in another application

A receiving application needs the exchanged package, this
[versioned profile](../spec/core-draft.md), its schemas and a supported CWL engine.
It needs no Wright parser, accepted canonical base, database or live session.
The [quickstart](quickstart.md) demonstrates installed packages consuming copied
artifacts outside this repository.

## The receiving sequence

```mermaid
flowchart LR
  P[Received package] --> R[Read and preserve bytes]
  R --> V[Structural and semantic validation]
  V --> B[Explicit local binding and preflight]
  B --> E[Existing CWL engine]
  E --> A[Verified MCP adapter]
  A --> O[Actual results and call records]
  O --> C[Quantity acceptance]
  C --> H[Separate approval state]
```

Opening/importing ends at inspection unless the user requests the later steps.
An unavailable dependency does not alter the package. An unsupported required
feature prevents claimed interpretation/execution but still permits preservation.
A known violated structural or semantic rule is invalid.

1. **Identify and preserve.** Resolve the RO-Crate root, profile and authoritative
   entrypoint. Validate safe package paths and inventory bytes. Keep received
   source bytes, unknown optional content and any original-source provenance.
2. **Validate meaning.** Check requirements schema separately from graph node,
   operation, binding, resource, output and acceptance references. Unknown
   required features or profile/workflow versions need explicit unsupported
   diagnostics. Unavailable MCP dependency versions are availability failures. JSON
   Schema alone cannot establish graph correctness or availability.
3. **Bind locally.** Match intended implementation/revision and application
   identity/version to receiving configuration and its stated trust basis. A
   URL, local UUID or same-named tool is not sufficient evidence.
4. **Preflight.** Negotiate MCP **2025-11-25**, observe capabilities and the
   required provider metadata, compare exact tool schemas and verify resource
   identity/revision. The mock's resource representation is a stated test
   contract; real CAD resources need a verified provider-specific adapter.
5. **Execute explicitly.** Preserve a source snapshot. After implementing the
   mandatory exchange requirement, create a distinct execution copy with only
   the consumed extension removed. Supply receiving `epx_context` and the local
   `epx-mcp-call` adapter. Delegate CWL graph, expressions, file staging and
   scheduling to the existing engine; do not invent missing edges in a wrapper.
6. **Inspect evidence.** Retain every successful upstream result and native
   failure cause. Check required outputs, actual call records and result hashes
   as well as engine outcome. Evaluate measured quantity criteria independently
   of execution state. The core never grants human approval.

## Use the installed CLI or library

The Python wheel bundles its schemas and installs `epx` and `epx-mcp-call`.
No repository-relative schema lookup is needed by a consumer. Its public CLI is
the simplest integration boundary:

```sh
epx inspect PROCESS_DIRECTORY_OR_ZIP
epx validate PROCESS_DIRECTORY_OR_ZIP
epx preserve PROCESS_DIRECTORY_OR_ZIP NEW_DESTINATION
epx preflight PROCESS_DIRECTORY_OR_ZIP --bindings LOCAL_BINDINGS.json
epx run PROCESS_DIRECTORY_OR_ZIP --bindings LOCAL_BINDINGS.json --engine cwltool --out NEW_RUN_DIRECTORY
```

`run --job LOCAL_INPUT_JOB.json` is the Python path's explicit run-input override;
the report records its bytes. It cannot supply the reserved `epx_context`.
The independent Node path currently uses the package's declared job.

Python integrations can use the installed modules directly:

```python
from pathlib import Path
from epx.package import open_root, load, preserve
from epx import jsonio, mcp
from epx.runner import run

with open_root("package") as root:
    process = load(root)
    print(process.summary())
    readiness = mcp.preflight(process, mcp.configuration(Path("local-bindings.json")))
preserve("package", "saved-package")
# Invoke only for an explicit execution action, after readiness succeeds.
report = run("package", "local-bindings.json", "run-python", "cwltool")
```

Python raises `epx.errors.Problem` with a `.diagnostic` for a known rejection.
The CLI serializes it. Keep the `open_root` context alive while using an extracted
ZIP package; closing it ends that temporary extraction.

The local npm package `epx-node-adopter` bundles its schemas, declares its ESM
exports and installs `epx-node`. A fresh consuming project can use its public API:

```javascript
import {
  loadPackage, inspectPackage, preserve, preflight, runPackage
} from 'epx-node-adopter';

const process = await loadPackage('package');
console.log(inspectPackage(process));
await preserve('package', 'saved-package');
const readiness = await preflight(process, 'local-bindings.json');
if (readiness.status !== 'available') throw new Error('Intended dependencies unavailable');
// Invoke only for an explicit execution action.
const report = await runPackage(process, 'local-bindings.json', 'run-node', 'streamflow');
```

The Node loader throws `Failure` with `.diagnostic` for known package errors;
preflight returns observations and diagnostics. Its CLI preservation syntax is
`epx-node preserve PACKAGE --out DESTINATION`. Both packages expose the same
portable facts and outcomes; incidental inspection-object layouts and detailed
diagnostic codes can differ. Do not import internal modules from the other
implementation to claim independent interpretation.

## The provider-adapter boundary

The graph invokes this named command with five explicit inputs:

```sh
epx-mcp-call --context CONTEXT_FILE --node main/volume --binding engineering --tool engineering.volume --arguments-json JSON_OBJECT
```

The command validates the node/binding/tool against the package and compares
arguments with the captured input schema. It rechecks intended provider,
protocol, application and required resources, makes the one declared MCP call,
then validates structured output. Successful `result.json` contains the original
MCP `CallToolResult`; it is not an invented universal engineering result shape.
The separate call record ties those bytes to run/node/provider/resources and
is retained before engine temporary files disappear.

The profile adds `_meta["engineering-process-provider"]` containing
implementation, revision, application, applicationVersion and executionPlatform.
The mock implements this contract. A real provider without it requires an
explicit verified adapter and corresponding evidence; the receiver must not
invent trusted metadata from a product name. Tool annotations are not an
identity or engineering-acceptance guarantee.

For a local fixture, the launcher digest provides a deliberately limited trust
basis; it does not attest the interpreter and whole dependency graph. A remote
binding needs an explicit configured-service trust subject and verified observed
identity. Credentials come from the receiving environment. Platform requirements
apply to the execution target, so a compatible remote instance may satisfy them.
Reachability alone cannot establish resource access or revision.

## Outcomes and replacement

Keep these fields separate in your product:

| Concern | States/meaning |
|---|---|
| Definition | Understood valid, known invalid, or unsupported required meaning |
| Readiness | Intended provider/resource/version available or unavailable |
| Execution | `succeeded`, `failed`, `unknown` or `blocked` |
| Acceptance | `pass`, `fail`, `indeterminate` or `not-run`, per criterion and overall |
| Approval | Separate subject-bound authorization; current core reports `not-requested` |

A lost response after a submitted mutation may mean the operation happened.
Retain that uncertainty, partial evidence and native cause. Never automatically
replay, infer rollback or approve the result. A `200`, process exit `0`, plausible
AI narrative or existing file is not sufficient success evidence.

Changing a verified connection to the same intended provider is local rebinding.
A different provider/application is an intentional new process revision. The
replacement helper accepts a **full intended binding** (the shape in
requirements), not local endpoints:

```sh
epx replace PACKAGE --binding engineering --with intended-binding.json --revision NEW_REVISION --out NEW_PACKAGE
epx-node replace PACKAGE --binding engineering --with intended-binding.json --revision NEW_REVISION --out NEW_PACKAGE
```

It preserves the graph and tool contracts and requires revalidation; it does not
translate provider-specific arguments, CAD geometry or resource identifiers.
Use an explicit authored mapping when those differ. The
[replacement example](../examples/calculation-replacement/README.md) shows the
simple same-contract case and requires new acceptance evidence.

## What an implementation may claim

Name the profile, versions, roles and tests actually passed. The tested pair
uses different existing workflow engines and separately written binders/adapters,
but shares public schemas, fixtures and lower-level CWL parsing libraries.
Repository-authored demonstrations do not establish outside organizational
adoption. Reader preservation is useful on its own; it does not certify execution.
The [Wright mapping](wright-compatibility.md) and real-CAD gate stay explicit.
