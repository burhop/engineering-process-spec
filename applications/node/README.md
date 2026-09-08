# Independent Node receiving application

This experimental application implements the core reader, binder, MCP adapter
and run/evidence path independently of the Python application and Wright.
StreamFlow interprets CWL and schedules tasks; these JavaScript modules do not
interpret the workflow graph. Both paths intentionally share the public schemas,
fixtures and upstream standards. They are repository-authored demonstrations,
not independent organizational adoption.

Install the locked JavaScript dependencies from the repository root:

```sh
npm ci --prefix applications/node --ignore-scripts
node applications/node/cli.mjs inspect examples/calculation
node applications/node/cli.mjs validate examples/calculation
node applications/node/cli.mjs preserve examples/calculation --out saved-calculation
```

Node 24 or later is required. Reader/preservation checks have run on Windows;
the full executor is tested on Linux in the pinned baseline image with Node
24.13.1 and StreamFlow 0.2.0rc2. Native Windows StreamFlow execution is not a
claimed tested platform. `EPX_PYTHON` may identify the explicitly installed
Python interpreter; otherwise `python` resolves from PATH. The driver verifies
StreamFlow's installed version before execution. No Wright services, modules,
credentials, CAD software or model-provider API is used.

After creating receiving configuration according to
[the binding schema](../../schemas/bindings.schema.json), run:

```sh
node applications/node/cli.mjs preflight examples/calculation --bindings local-bindings.json
node applications/node/cli.mjs run examples/calculation --bindings local-bindings.json --engine streamflow --out run-calculation
```

The output directory must be empty. A successful calculation reports execution
`succeeded`, two named MCP call records, volume `0.00002 m3`, mass `0.157 kg`
and acceptance `pass`. Preflight inspects protocol identity, exact tool schemas
and required resources and makes zero engineering calls. Missing or mismatched
bindings produce `unavailable`. Opening/preserving needs no binding file and
starts no provider process.

For a reproducible maintainer smoke run using the already built
[baseline image](../../experiments/workflow-baseline/README.md):

```sh
docker run --rm -v "$PWD:/workspace" -w /workspace eps-workflow-baseline:20260907 node applications/node/smoke.mjs /workspace/.work/my-node-smoke
```

Use a new output directory for each run. The smoke script explicitly configures
the test-only provider, verifies its launcher SHA-256 against the public fixture,
and invokes the real StreamFlow/MCP path. It does not represent Solid Edge.

## Interface for another project

The small modules are reusable without importing Wright or the Python adapter:

| Module | API and result |
|---|---|
| `package.mjs` | `loadPackage(path)` validates a directory/ZIP and returns package facts; `inspectPackage(package)` produces serializable inspection; `preserve(source,destination)` copies original bytes without interpretation. |
| `cli.mjs` | `preflight(package,bindingsFile)` returns observations/diagnostics; `runPackage(package,bindingsFile,outDirectory,'streamflow')` returns the report and writes `report.json`. |
| `mcp.mjs` | Independent MCP2025-11-25 stdio and HTTP JSON client plus intended-provider/resource resolver. This is the adapter boundary, not a universal CAD adapter. |
| `mcp-call.mjs` | `invoke({context,node,binding,tool,arguments_json})` verifies the invocation, makes one engineering call and writes its evidence. |
| `replacement.mjs` | `replaceBinding(source,{binding,replacementFile,revision,outDirectory})` creates an explicitly revised package with prior requirements provenance and an impact report. |

A consuming local project installs a locally built tarball and imports the
public API. The tarball contains this draft's matching schemas; ordinary
installed use needs no checkout or schema-path environment variable:

```sh
npm install --ignore-scripts /absolute/path/to/epx-node-adopter-0.1.0-draft.1.tgz
```

```js
import {loadPackage, inspectPackage, preserve, preflight, runPackage} from 'epx-node-adopter';
const processPackage = await loadPackage('./received');
console.log(inspectPackage(processPackage));
await preserve('./received', './saved');
const readiness = await preflight(processPackage, './local-bindings.json');
if (readiness.status === 'available') {
  const report = await runPackage(processPackage, './local-bindings.json', './run', 'streamflow');
  console.log(report.execution, report.acceptance);
}
```

The developer supplies `received` as an exchanged directory or ZIP and
`local-bindings.json` as receiving configuration. Neither comes from hidden
Wright state. A fresh offline npm consumer has successfully validated and
preserved a separately copied calculation package using these installed exports
and bundled schemas, with no `EPX_SCHEMA_ROOT` override. Public registry
publication and this project's redistribution/contribution terms remain
undecided.

Maintainers create the tarball from this application's directory:

```sh
npm ci --ignore-scripts
npm run build
npm test
npm pack --pack-destination .work
```

Create `.work` first if it does not exist. `prepack` automatically repeats the
deterministic schema-copy build. Root `schemas/` remains the sole hand-edited
authority; generated `applications/node/schemas/` copies and their digest
manifest must never be edited separately. `npm run check:schemas` rejects drift.
The installed runtime resolves its bundled schemas through its own module URL.
`EPX_SCHEMA_ROOT` remains an explicit development override, not an installation
prerequisite. `test/installed-consumer.mjs` is a repeatable consumer probe: copy
it into a fresh project containing the installed tarball and a `received`
calculation package, then run `node consumer.mjs`. It asserts that API resolution
is inside that consumer's `node_modules`, validates bundled schema hashes, and
writes `installed-consumer-report.json` after a byte-preserving save.

The driver makes an immutable source snapshot, consumes only the implemented
`ExchangeRequirement` in a separate ephemeral execution copy, and records both
workflow digests. It supplies `epx_context` and puts its implementation of
`epx-mcp-call` on the engine PATH. CWL still supplies inputs, expressions and
connections. StreamFlow may exit zero for some failures; the driver also
requires exactly one successful result for every declared node. It separately
reads the engine's actual final-output JSON, verifies every declared output is a
readable retained File, resolves its `outputSource`, and checks its bytes against
the producing call's evidence. Successful calls alone cannot replace missing
workflow outputs.

The command-level adapter contract is:

```sh
epx-mcp-call --context CONTEXT_FILE --node main/step --binding engineering --tool engineering.volume --arguments-json JSON_OBJECT
```

It writes the original CallToolResult JSON to `result.json` on success and
copies observed result evidence to the run's `artifacts/` before engine cleanup.
Independent call records are written under `calls/`. A failed downstream step
does not remove successful upstream records. A lost mutation response produces
unknown outcome without automatic replay. Execution and engineering acceptance
are separate; human approval is `not-requested` because this core implements no
human authorization service.

Diagnostics use the common schema's category and requirement IDs. CLI JSON
outputs contain diagnostics for invalid/unsupported packages; preflight/run
return nonzero when unavailable or execution/acceptance fails. A report with
partial acceptance is not an accepted result. The bounded ZIP reader rejects
duplicate members, path escapes and symlinks; limits are 10,000 files,
32 MiB per ordinary file and 128 MiB total ZIP expansion. Limit violations are
unsupported, not proof a definition is semantically invalid.

## Explicit provider replacement

This deliberately narrow editing command retains the source and creates a new
process revision. `replacement.json` contains the full intended binding
descriptor shaped like `requirements.bindings.engineering`, rather than local
connection configuration:

```sh
epx-node replace received --binding engineering --with replacement.json --revision 2 --out revised
```

The graph, tool descriptors, argument/data connections and resource mappings
remain byte-preserved. The command updates only the selected intended binding
and process revision, retains the previous exact requirements as a hashed
provenance artifact, adds a change report and revalidates the new package. The
report identifies direct and downstream affected nodes, acceptance criteria and
resources; previous results and approvals cannot establish acceptance of the
new revision. It makes zero engineering calls and claims no provider equivalence.

The receiving application must preflight the new intended provider/resources
and generate new execution and acceptance evidence. Changing tool names,
schemas, resource mappings or CAD operations requires separately authored,
reviewed changes; this command is not a general CAD converter.

## Checks and dependency notices

```sh
npm test --prefix applications/node
```

The unit tests exercise strict JSON, byte preservation, unknown required
features, digest tampering and semantic errors. Full independent MCP behavior
belongs to the shared black-box conformance suite; a unit-test pass alone does
not certify the advertised execution core.

Direct dependencies are pinned by `package-lock.json`: Ajv 8.18.0 (JSON Schema
2020-12) and yauzl 3.2.1 (bounded ZIP reading). The core uses packed CWL JSON;
YAML serialization is outside this initial profile.
Their upstream notices remain in the installed packages. See
[dependency attribution](THIRD_PARTY.md); no project license is selected here.
