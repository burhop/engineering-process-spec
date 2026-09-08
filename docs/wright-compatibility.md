# Wright compatibility and Solid Edge capture

Mapping revision: **wright-080-20260907.1**, informational. This maps the
observed Wright contracts and source to the implementation goal's required
portable core. [Decision 003](../decisions/003-cwl-core.md) selects CWL v1.2
for the experimental executable representation. This map does not certify
`.wflow` conformance or claim a working Wright-to-CWL converter; actual
conversion still requires explicit authoritative inputs and independent tests.

The [read-only evidence inventory](../research/wright.md) records exact commits,
paths, uncommitted SHA-256 identities, observation times and limitations. Its
22:39 UTC refresh supersedes earlier native-execution observations. The active
checkout is `D:/repos/wright/.local-run/epp-f02b-writer/wright`, HEAD
`87706742e62af82fa5a43f147b59e6d98e105024`, with substantial uncommitted code.
Wright and the locally inspected SolidEdgeMCP checkout remain unchanged by this
project. No Wright application or test was launched for this work.

## What a receiving application needs

A source file is insufficient when some of its meaning lives in the author's
application state. Wright's checked-in canonical contract is
`workflow-ir` / `2.0.0-recovery.1`. Its engineer-facing source reconstructs
bindings and some vocabulary using an accepted canonical base. Its native
compiler independently interprets some settings from `.wflow`. These are three
related surfaces, not a demonstrated interchangeable file format.

The receiving application needs one authoritative draft process, all referenced
schemas and input artifacts or identified resources, and local binding
configuration. The exchanged process must carry the intended implementation,
application provider, operation and resource requirements. The local binding
supplies endpoint/launch details, receiving paths and credentials. It cannot
quietly choose the server default or reinterpret a provider as a capability.

For example, the recorded Wright CAD source contains server UUID
`965a99c8-130d-4e64-96b0-18db066027b0`, an AI task, a model path and desired
thickness. A receiver cannot derive a portable implementation revision, input
model digest, application version or deterministic call sequence from those
facts. A trace establishes what one execution did; it does not make that trace
equivalent to every permitted execution of the AI task.

## Feature mapping

“Direct” below means the concept has an unambiguous core counterpart once its
facts are explicitly present. “Translation” needs an explicit validated mapping.
“Preserve-only” retains the original without claiming core execution. “Wright
change” names a future integration change that this repository does not make.
No row is evidence of a completed Wright importer/exporter.

| Wright feature and source | Classification | Mapping obligation or gap |
|---|---|---|
| Original UTF-8 `.wflow` bytes; `workflow_sources.py` | Direct preservation | Retain original bytes and SHA-256 as source provenance. Wright's local storage journal/layout are not a portable execution graph. |
| Canonical blocks, ports, relationships and artifacts; recovery schema | Translation | One supported acyclic subset may map to existing workflow tasks/data handoff. Preserve stable source-to-target IDs and report unsupported connections/types. Do not publish canonical and translated graphs as competing authorities. |
| `parseAuthoring(text, acceptedBase)` and `tool.assignment` | Wright change / translation | Export must supply the exact canonical facts needed by the source, or an already resolved portable process. A fresh receiver has no accepted base to consult. |
| Fixed `mcp-tool` task settings | Translation | Resolve local `mcp_server`, aggregated name and local digest into an explicitly declared implementation identity, upstream tool name, protocol and captured contract. Preserve arguments, connected inputs and result mapping; prove data conversion instead of assuming string/JSON equivalence. |
| Binding `provider_id`, `server_id`, `tool_id`, `schema_digest`, `argument_map`, `result_map` | Translation / Wright change | These existing fields inventory necessary facts, but identity/version scope differs. The native digest includes local server ID and adapter metadata, so it cannot be reused as a portable schema-only digest. |
| Native fixed resolver matching tool plus selected server | Direct policy | A compatible adapter must still match all intended portable identity facts, then record receiving-instance resolution. A same-named tool on another server is insufficient. |
| CAD `cad.list_providers` and `isDefault` selection | Wright change | Persist explicit application provider selection; export `solid_edge` when that was the author's choice, and pass it to every relevant call. A changed default must not change the process. |
| AI prompt/MCP task, model policy, bounded agent loop | Preserve-only | The first fixed-call core does not promise equivalent reasoning. A deterministic sequence derived from observed calls is a newly authored variant with provenance and acceptance criteria. |
| CAD working-copy/save/export settings | Translation | Map copy policy, isolated paths, exact resource identity and selected representation into explicit operations supported by the verified provider contract. An export file is not automatically equivalent to the native model. |
| `EngineeringResult`, `Representation`, `Provenance` | Translation | Preserve kind, format, durability, provider/resource/revision, digest/size, run/task/output and input revisions. Session handles remain run-local; persistent exported bytes or verified resource revisions are required for later independent execution. |
| Application-resource handoff and import/export adapter | Translation / preserve-only | Preserve declared adapter identity and explicit export/import path. Core support requires a separately implemented adapter and conformance cases for its resource semantics; a generic JSON copy cannot establish that. |
| Recovery approval block or binding approval policy | Preserve-only | Core preservation does not implement a human approval workflow. A portable approval profile must bind the decision, actor/role and exact definition/result revisions and test stale approvals. |
| Native design-check `approval`/`revision` edges | Preserve-only | These now implement bounded agent verdict/rework behavior in source. They do not demonstrate human approval; exporting them as human approval would change semantics. |
| `workflow_run_record.py` events and partial results | Translation | Preserve source digest, attempts, partial results and errors. Map execution, acceptance and human approval separately. A completed native run is not automatically an accepted engineering result. |
| Wright async-operation metadata and cancellation | Preserve-only unless profiled | Its `wright/operation` adapter includes status/result/cancel tools. A core executor must reject unsupported required operation behavior while preserving the process; request cancellation is not confirmation a mutation stopped. |
| Groups, layout and unsupported components/control constructs | Direct preservation / preserve-only | Layout may be nonsemantic; components or control constructs cannot be treated as layout. Preserve originals and report executable-subset gaps. |

## External adapter inputs and outputs

The working external capture utility is
[`tools/wright_capture.py`](../tools/wright_capture.py). It has no third-party
dependencies and does not import Wright modules or parse `.wflow` with an
approximate grammar. It reads only explicitly supplied files, preserves their
exact bytes and reports supplied/missing facts. Its output is a capture folder,
**not a conforming or executable core package**. Run it from this repository:

```sh
python tools/wright_capture.py original.workflow.wflow --out artifacts/local/new-capture
python tools/wright_capture.py original.workflow.wflow --canonical canonical.json --binding-facts binding-facts.json --out artifacts/local/new-capture-with-context
```

Use a new destination each time. The utility refuses an existing destination
and any resolved output beneath `D:/repos/wright`. For an additional Wright
checkout or container mount, append `--wright-root /absolute/read-only/root`;
this adds a protected root and never removes the default protection. It does
not follow file references found inside companion JSON. Invalid optional JSON
is preserved and diagnosed. Inputs exceeding the tool's 16 MiB capture limit
are refused without producing an alleged export.

The output contains `original.workflow.wflow`, optional
`canonical.original.json` and `binding-facts.original.json`, plus
`capture-report.json`. The report identifies original/preserved files and
SHA-256 values, recognized canonical version fields, supplied binding assertions,
missing facts and preserved unsupported semantics. Reading the known canonical
header does not validate the complete canonical schema or prove correspondence
with the original source. A supplied digest association is labeled
`author-asserted-match`, never semantic equivalence.

The optional fact file is an advisory capture input. For the named CAD case,
the following deliberately incomplete example retains known identities while
leaving uncaptured values null:

```json
{
  "format": "epx-wright-binding-facts",
  "version": "0.1.0-draft.1",
  "sourceSha256": null,
  "canonicalSha256": null,
  "bindings": {
    "965a99c8-130d-4e64-96b0-18db066027b0": {
      "implementation": {
        "id": "https://github.com/burhop/SolidEdgeMCP",
        "revision": null
      },
      "application": {"id": "solid_edge", "version": null},
      "protocolVersion": null,
      "toolContracts": [],
      "resources": []
    }
  }
}
```

Fill these fields only from explicit evidence. `toolContracts` and `resources`
may hold captured artifact/revision references; the inspector preserves those
assertions but deliberately does not open referenced files or contact a provider.
Do not put credentials in the fact file. A fully populated capture still cannot
turn an AI-directed CAD task into an equivalent fixed-call CWL process.

Focused verification is reproducible with:

```sh
python -m unittest discover -s tests -p test_wright_capture.py
```

The tests check exact preservation, missing facts, malformed companions, explicit
file-only access, protected outputs and refusal to overwrite existing work.

An adapter implemented outside Wright can safely inspect explicitly supplied
files. It must neither import Wright modules nor read an author's database,
secret store or live sessions to silently complete missing facts. A conversion
attempt needs these explicit inputs:

| Input | Required content | If absent |
|---|---|---|
| Original source | Exact `.wflow` bytes, source kind, observed source SHA-256 | Refuse to claim source-preserving conversion. |
| Canonical context, when source requires it | Exact exported recovery JSON, schema version, digest and relationship to that source | Report unresolved assignments/vocabulary; retain source as preserve-only. |
| Provider mapping | Local server UUID mapped by the author to intended publisher/repository, exact implementation revision, application provider and app contract/version | Report missing identity; never infer it from a display name, UUID, URL reachability or default. |
| Captured contracts | Actual negotiated MCP version and complete tools/list input/output schema bytes for each selected upstream tool; capture/binary identity | Report missing contract; do not synthesize a schema from an old trace. |
| Resource manifest | Rights/authority to use the supplied artifact, exact input bytes/digest or provider resource/revision, expected representations | Report missing/inaccessible/revision-unverified input. |
| Authored execution variant | Explicit supported tasks, data mapping, acceptance criteria and acknowledged losses for AI-directed/richer input | Preserve-only; do not label a captured call sequence equivalent. |
| Receiving configuration | Connection or executable path, permitted workspace paths and credentials supplied locally | Valid supported definition can remain unavailable for execution. |

The adapter's output should be an inventory/loss report and, only when complete,
a profile process plus original-source provenance. Report each source feature's
status, source-to-target IDs, supplied identity evidence, missing facts and
intentional changes. If no complete executable conversion is possible, producing
an honest preservation package/report is useful, but is not independent
execution evidence. A mapping stub must never fill an unknown real version with
an invented example value.

## Real Solid Edge capture gate

Status: **real-provider execution unverified for this profile**. The historical
Wright readback is evidence for one same-installation result, not a runnable
portable fixture or independent executor test. A usable provider exists in local
source, but this inspection did not capture a running binary/contract or establish
redistribution rights to the model. Do not call a mock Solid Edge.

Verified identity clues are intentionally limited:

- Local repository origin: [burhop/SolidEdgeMCP](https://github.com/burhop/SolidEdgeMCP).
  Observed HEAD `f58a783d2bfad4cff97c818bb63d42c1485d305a` has uncommitted
  provider/tool changes; its exact file hashes are in the evidence inventory.
- Application-provider ID in source: **`solid_edge`**; display name `Solid Edge`.
- Provider project dependency: C# `ModelContextProtocol` **1.4.0**,
  target **`net10.0-windows`**. This is not a claim of the live application's
  version or of protocol compatibility with every MCP revision.
- Historical trace, already identified by digest: `cad.get_server_info` reports
  `solid-edge-mcp` **0.2.0**; the edit's observation context reports provider
  **`1.0.0+f58a783d2bfad4cff97c818bb63d42c1485d305a`** and Solid Edge
  **`226.00.01.04`**. These are self-reported values from the September 7 run,
  not a current frozen build or evidence of application compatibility ranges.
- Actual intended operation: change **`MaterialThickness` to 2.5 mm** in an
  isolated copy, read it back within **0.001 mm**, pass that exact result to
  another task, then export STEP. The older trace includes `providerId: solid_edge`.

The opt-in integration sequence, after the missing inputs are supplied, is:

1. Freeze a provider build identity including uncommitted changes if used, record
   its executable/dependency digests, configured mode and permitted isolated
   output root. Capture actual initialize negotiation, tools/list, explicit
   provider listing and application status/version. Keep connection credentials
   and machine-specific paths in receiving configuration. Use a protocol profile
   the actual capture and both executors support.
2. Obtain an authorized simple native sheet-metal input. Record its provenance,
   digest and expected precondition; preserve the original. Publish input bytes
   only when their use and redistribution terms are settled. A content hash alone
   does not supply rights or make the file available.
3. Author the fixed-call variant explicitly. The observed source supports
   `cad.open_document`, native `cad.save_document` with copy semantics,
   `cad.list_variables`, `cad.set_variable`, `cad.rebuild_document` and
   `cad.export_document`. Verify their actual captured schemas before authoring
   arguments. Always bind `providerId: solid_edge`, the returned exact
   `documentId`, and use explicit non-active selection where the tool exposes it.
4. Read variables from the working copy. The current `cad.set_variable` signature
   requires `variableName`, `desiredValue`, `desiredUnit`, fresh `expectedValue`,
   `expectedUnit`, `expectedFormula` and `confirmationToken`. For the proposed
   value the documented token is `set_variable:materialthickness:2.5:mm`.
   This provider token is a request precondition, not evidence of a human review.
5. Rebuild and read the same document after mutation. Verify thickness, revision
   continuity, original-file digest and expected native/export artifacts. Record
   only checks actually performed; STEP creation is not AP242 conformance or
   geometric/manufacturing acceptance.
6. Run the exact package through both independent executors with isolated output
   directories. Compare provider identity, argument/data handoff, resource
   continuity, measured evidence and retained partial results. Then transfer to
   an installation with no compatible local or remote provider: opening/saving
   must preserve bytes; preflight must explain unavailability and make zero
   engineering calls. A compatible configured remote instance may satisfy the
   same provider requirement; another CAD implementation requires a new process
   revision and revalidation.
7. Exercise export failure after a successful native save and a deliberately lost
   mutation response in an isolated provider test environment. Retain partial
   outputs; mark the uncertain mutation outcome; inspect before any explicit
   retry. Never infer rollback or safe replay from a timeout or cancellation.

This is a capture/integration recipe, not a runnable real-CAD command or a claim
that the missing contract can be guessed. Prerequisites remain the frozen build
and actual schemas, supported execution/permissions, authorized model bytes,
explicit authored variant and an isolated integration environment. Simulated
provider tests cover the portable binding/protocol rules separately.

## Future Wright work and import expectations

Wright export would need to persist intended provider/application identity,
publish all authoritative source facts, resolve local resource references into
identified artifacts/resources and emit a conversion report. It must preserve
original AI tasks when offering a fixed-call authored variant. Its local storage
journal should remain local; an imported process gets new local storage identity
while retaining the exchanged definition revision and provenance.

Wright import would need to recognize the profile/version, preserve unknown and
unavailable content, render dependency diagnostics, and bind verified receiving
instances without changing the process. It must not silently reconstruct missing
meaning from a mounting-bracket default model, select a different server's same
tool name, or use a changed CAD default. Import/edit/save and explicit replacement
need tests through the real UI in a later authorized Wright implementation task.

Priorities are to capture identity/contracts first, export a supported fixed-call
case second, and prove unavailable-provider round trips plus real-CAD handoff
third. Rich AI tasks, automatic rework and human approval need separately bounded
profiles and independent evidence before claiming portable execution.
