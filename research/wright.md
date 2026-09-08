# Wright: read-only implementation inspection

Observation date: 2026-09-07. This is an inventory, not a claim of production
conformance. **Contract** means a checked-in contract; **source** means code
inspected without executing it; **recorded** means existing run evidence read
and cross-checked; **proposal** means work this repository recommends.

The initial observation below is retained as history. The [implementation-goal
refresh](#implementation-goal-refresh) records changed native code observed at
22:39 UTC on the same day; use that refresh and the
[compatibility map](../docs/wright-compatibility.md) for current mapping work.

## Active checkout and limits

The active native API and workflow UI were confirmed through Windows process
command lines, not a planning document:

- Root: `D:/repos/wright/.local-run/epp-f02b-writer/wright`.
- Branch: `codex/080-canonical-workflow-recovery`.
- HEAD: `87706742e62af82fa5a43f147b59e6d98e105024`, dated 2026-09-02,
  `docs(workflows): close verified image-led authoring delivery`.
- Vite PID 38744 loaded this checkout's Vite executable on port 5227.
  Python PIDs 14456 and 42728 loaded this checkout's virtual environment with
  `uvicorn api.main:app` on port 8018. Gateway processes used the same environment.
- Another Vite process served `D:/repos/wright` on 5173, and Docker listed
  `wright-native-ui-preview`. Thus “Wright is running” alone does not identify
  the implementation. No claim is made that the preview container matches this
  checkout, or that every running Python module reflects the newest disk edit.

The root checkout's HEAD was `1ada5de0aaa608baadafa41031e5877eb685bed3`;
it is not the research baseline. The active checkout contains modified and
untracked implementation files. The appendix records exact bytes observed;
HEAD alone cannot reproduce this working tree. Observations are not an atomic
snapshot of all concurrent work.

Only filesystem, Git, process, and container metadata reads were performed.
No Wright applications were started, tests run, or files changed. Temporary
test directories denied enumeration under the sandbox; they were unnecessary
for this inspection. Process metadata was obtained through an approved
read-only escalation. Git ownership checking used a command-local
`safe.directory` value; no Git configuration was changed.

## Contracts versus executable paths

| Subject | Evidence and meaning | Portability implication |
|---|---|---|
| Canonical definition | **Contract:** `canonical-workflow-ir.schema.json` declares `workflow-ir`, version `2.0.0-recovery.1`; stable blocks, ports, relationships, artifact contracts, bindings, and components. Bindings include provider/server/tool identity, schema digest, argument/result maps, and approval policy. Root objects are closed. | Useful inventory of semantic facts; recovery names and schemas are not a stable independent standard. Unknown required fields are rejected rather than interpreted. |
| Source and authoring | **Contract/source:** `conformance-kernel.md`, `recovery-authoring.ts`. Engineer source omits host identities and rehydrates against the exact accepted canonical base. Its `tool.assignment` resolves against existing bindings. Unknown source fields and assignments produce diagnostics. | The engineer-facing source is not by itself a self-contained export of the whole canonical definition. An export needs every authoritative fact or an explicitly bounded subset. |
| Storage | **Contract/source:** `workspace-workflow-source.md`, `workflow_sources.py`. Visible `workflows/<slug>.workflow.wflow` bytes, compare-and-set saves, and separately versioned layout. | Opaque storage preservation is useful, but it does not prove an unfamiliar block can be opened, edited, and saved through every editor path. |
| Native execution | **Source:** API router imports and calls `prepare_prompt_workflow` and `execute_prompt_workflow`; `workflow_source_execution.py` has a separate parser/compiler. It accepts 1–32 supported prompt/MCP work tasks, checks connections and source digest, and rejects unsupported execution types. | Do not infer executable approval/decision/feedback semantics from the broader canonical model. Frontend canonical validation and native source compilation are distinct implementations to reconcile and test. |
| Fixed MCP tool block | **Source:** `workflow_mcp_execution.py`, `resolve` and `preflight`. Resolution requires the selected server ID and gateway tool name. A missing tool or changed digest raises a readiness error; arguments use Draft 2020-12 validation. | This path does not search for a substitute provider. However, the saved server ID is an installation identifier, not demonstrated portable publisher identity. |
| MCP contract digest | **Source:** `schema_digest` hashes local server ID, aggregated tool name, input/output schema, server revision, approvals, and optional Wright adapter metadata. | It is broader than a schema hash and includes local context. Rebinding the same provider can change it. A portable digest must have an explicit scope and a reviewed mapping from this implementation. |
| MCP protocol | **Source:** `gateway_service.py` declares `SUPPORTED_PROTOCOL_VERSION = "2025-11-25"`; the native runtime initializes a session. | Current source does not establish support for MCP 2026-07-28's changed lifecycle. Keep protocol version separate from SDK, server, CAD application, and process versions. |
| Agent-driven MCP task | **Source:** `task_tools` limits tools to one selected server; `run_task` bounds calls/time and requires successful call evidence. | AI task policy and model behavior are additional semantics. Successful calls do not establish engineering acceptance. Do not export such a task as a fixed call sequence and claim equivalence. |
| CAD adapter | **Source:** `workflow_cad.py`, `cad_capabilities`, selects the non-fake provider marked `isDefault` by `cad.list_providers`. Later calls inject that provider and reject an attempted different provider. | Session-level consistency is present, but author-selected provider persistence is not established. A changed server default is a concrete risk for the portable contract. This observation does not mean the fixed MCP tool resolver substitutes tools. |
| Results/resources | **Source:** `workflow_results.py` distinguishes values, workspace files, application documents, cloud resources; includes provider/resource IDs, optional revision, durability and provenance. `select_representation` filters by explicit input requirements. | Strong foundation. Current provider strings can include the installation's server ID; optional revision and transient handles need explicit exchange rules. |
| Failure records | **Contract:** `run-records.md` explicitly describes simulated recovery records. **New untracked source:** `workflow_run_record.py` persists activity/partial results and records failed or cancelled execution. | These are different contracts. The existence of new code does not retroactively make the recovery wire schema accept `cancelled`; that schema's states differ. |
| Packaging | **Source:** `workflow_campaign_fixtures.py` builds digest-checked `development-fixtures` bundles and restores missing files while rejecting conflicting content. Its own limitation says application identities and credentials are not portable. | A useful test-fixture mechanism, not evidence of portable executable process packaging. |

Committed contracts are available at the [exact Wright revision](https://github.com/burhop/wright/tree/87706742e62af82fa5a43f147b59e6d98e105024/specs/080-canonical-workflow-recovery/contracts).
Uncommitted findings above are located by the hashes below, not attributed to
that commit's contents.

## Engineering examples and existing evidence

**Recorded CAD case.** The bundled `cad-result-handoff.workflow.wflow` has
source SHA-256 `db094563ebde16e1229e119f9f87dcc573ed2db3e3dce62b3dff137ce0134f36`.
It asks for a working copy of `cad-test/bracket.psm`, changes
`MaterialThickness` to 2.5 mm, passes the upstream model to another task, and
exports STEP. Its settings retain MCP server UUID
`965a99c8-130d-4e64-96b0-18db066027b0`; they do not name a portable publisher
or pin an application version.

The original `live-handoff-corrected.json` trace contains calls with
`providerId: solid_edge`. The campaign recheck
`recheck-b1709fa526c34140bc47616f72905a63.json` references that trace and the
same source digest. It reports 2.5 mm readbacks in both tasks within 0.001 mm,
native and STEP file structure/digests, and preservation of the original file.
The original run started at `2026-09-07T15:44:12.362596+00:00`; the recheck is
dated `2026-09-07T16:17:25.950106+00:00`. It explicitly retains
`engineering_review_required: true` and `user_accepted: false`.

This supports a **recorded same-installation Solid Edge result with narrow
assertions**. It does not demonstrate a receiving installation, an independent
executor, geometric equivalence of exported STEP, AP242 conformance, manufacturing
fitness, or user acceptance. No CAD call or recheck was rerun for this research.
The fixture's STEP export is named `step`; the recovery model's AP242 label is
not evidence of which application protocol the live export used.

**Source tests.** `test_workflow_mcp_execution.py` uses a fake gateway and asserts
no calls for disabled tools, changed bindings, or bad inputs. These are useful
test definitions, not fresh passing results. `workflow_campaign_oracles.py`
checks CAD readback after mutations and exact unit/tolerance comparisons;
its analysis checker also ties a quantity to provider/resource revision and a
recorded inspection call. It does not implement general unit conversion.

**Conceptual examples.** `model.ts` includes a mounting-bracket model with
`server.solid-edge`, placeholder tool IDs/digests, manufacturing checks and
review. The native compiler's supported work-task restriction prevents treating
this as an implemented human approval workflow. The calculation and inspection
approval cases in [the test design](../use-cases/interoperability.md) remain
proposals except for the specifically identified CAD observations above.

## Gaps to carry into the specification experiment

1. Separate intended provider identity from local server/connection identifiers;
   include application provider identity inside multi-provider MCP servers.
2. Separate invalid source, unsupported required semantics, and unavailable
   execution prerequisites in portable diagnostics. Native `WORKFLOW_NOT_READY`
   currently groups several of these reasons.
3. Prove no-op preservation through UI import/save with unavailable tools and
   unknown blocks. Storage and parser tests alone cannot prove this.
4. Define evidence for contract-compatible rebinding, explicit replacement,
   resource revision checks, and post-failure recovery. No such cross-installation
   demonstration was found in the inspected fixtures and traces.
5. Reconcile the canonical contract, source authoring, native compiler and durable
   run records before publishing a portable mapping; version every intentional
   difference. Preserve richer Wright source when only a subset is exportable.

## File identities

The following table is generated from read-only file hashes in the active
checkout. `HEAD` means byte-identical to the tracked file; `working tree` includes
modified or untracked content. Paths are relative to the confirmed root above.

Hash observation (UTC): 2026-09-07T18:33:25.1840086Z

| Path | Content | SHA-256 |
|---|---|---|
| `specs/080-canonical-workflow-recovery/contracts/canonical-workflow-ir.schema.json` | HEAD | `7e266a96b850470aa1821fc0d771a6f0254e2414b7c2bc91b637293b2a1c936a` |
| `specs/080-canonical-workflow-recovery/contracts/conformance-kernel.md` | HEAD | `9b6f87b3d5562b7cf716c9b8b66ce9bb199e8313f01bd04077bd4f7649fc8c42` |
| `specs/080-canonical-workflow-recovery/contracts/workspace-workflow-source.md` | HEAD | `669c83643f7a0a183a588c7df65174872d001a90e145a89b778b70a59c08ccda` |
| `specs/080-canonical-workflow-recovery/contracts/run-records.md` | HEAD | `efaf47e50ddad8d16e324246e8fe556dab4b1efbe5dcd4f9b3e88e30a2956d9e` |
| `apps/web/src/prototypes/workflow-recovery/model.ts` | working tree | `ea62ab00243100ce9a9a62e3515631351bb364d5d715554b5b0797ec12903274` |
| `apps/web/src/prototypes/workflow-recovery/recovery-authoring.ts` | working tree | `073acd54018378f05ac801065560c8fbeeab2f3b8f8721a096a347f5e8049faf` |
| `apps/api/src/api/routers/workspace.py` | working tree | `da5e95e307616b00dbac04628d5fc33991ffe4390200aa07ce1b3ebe2b6fd9bd` |
| `packages/tool_registry/src/tool_registry/gateway_service.py` | HEAD | `787b7461a800fcaa274c98ceaed9c0e77ac0108f8250dd35f2241a9adfc2fd10` |
| `packages/workspace_service/src/workspace_service/workflow_sources.py` | HEAD | `92c79666bfd703fd3aa03a0aca3aa27201089a7938fc74f7370afa4a3a9b2055` |
| `packages/workspace_service/src/workspace_service/workflow_source_execution.py` | working tree | `1716f70d5894a6f700e7e0d7812a9f997b4c018da7260a88ecfd086dd622b589` |
| `packages/workspace_service/src/workspace_service/workflow_mcp_execution.py` | working tree | `32ff1889e237c155641c5c62937b542d3a089a1f4169421a592ac38e7f897eb7` |
| `packages/workspace_service/src/workspace_service/workflow_cad.py` | working tree | `804cba407f0e623e54cdab2efab7fd6dff35c2ef243d2eecb5f0b6f0f8f3dff4` |
| `packages/workspace_service/src/workspace_service/workflow_application_task.py` | working tree | `7d543984407410dac024fcddbc25a58119c404f1a4cefda00057782bced4dedb` |
| `packages/workspace_service/src/workspace_service/workflow_results.py` | working tree | `7c6974163ca67cc74c00816444a5fb249264291a8a2ac55b0d9656db394f2361` |
| `packages/workspace_service/src/workspace_service/workflow_run_record.py` | working tree | `29d728e2ed7928b428326faed621d2a11c4d181ff75dce29ceedf4dc0551ed82` |
| `packages/workspace_service/src/workspace_service/workflow_campaign_fixtures.py` | working tree | `1e2a5d92a5d2d17ed1db1b0acee44cb902beeb61bf75310843ced93c382e2ba2` |
| `packages/workspace_service/src/workspace_service/workflow_campaign_oracles.py` | working tree | `d7c40ce0d4e06c8b7dcb373b17d3b4a9a6eb19cc8c746fd17cc703115e4f7f76` |
| `packages/workspace_service/tests/test_workflow_mcp_execution.py` | working tree | `98c2b2fa1488e83969bd8dda7cb8c63c01fec34bae2f255b80da35c6644846e1` |
| `artifacts/workflow-campaign/fixtures/smoke-20260907/files/workflows/cad-result-handoff.workflow.wflow` | working tree | `db094563ebde16e1229e119f9f87dcc573ed2db3e3dce62b3dff137ce0134f36` |
| `artifacts/workflow-campaign/oracles.json` | working tree | `8cbaedd6241ef4bce22034025cde3e29bd6922ec0ae7131318f6b57f72ecbf66` |
| `artifacts/workflow-campaign/attempts/recheck-b1709fa526c34140bc47616f72905a63.json` | working tree | `f63e34c3fe716eb7dbe7527f42c284b7128b40906cafaefe14f50533218d2cd0` |
| `artifacts/ui-walkthrough/cad-deliverables/2026-09-07T15-30-02-145Z/trace/live-handoff-corrected.json` | working tree | `ba99e3a9628bd9c8f64d658a47aea04bae4c15246ab3a706dffde142a1c82f01` |

## Implementation-goal refresh

Read-only refresh: 2026-09-07T22:39:06Z. Process command lines reconfirmed the
same active checkout, branch and HEAD. Vite PID 38744 still used its executable
on 5227; API PIDs **7220 and 18032** now used its virtual environment with
`uvicorn api.main:app --host 127.0.0.1 --port 8018`. The root Vite on 5173 was
also present. This identifies the checkout, not which uncommitted disk bytes
each long-lived module had loaded. No Wright or provider application/test was
started, stopped or modified for this refresh.

The four recovery contracts, frontend `model.ts` and `recovery-authoring.ts`,
API router, gateway service, opaque source store, result model, campaign fixture
builder and oracles retained their earlier hashes. The recorded CAD source,
trace and recheck also retained their earlier hashes. Other native files changed:

| Changed or newly inspected path, relative to active checkout | SHA-256 at refresh |
|---|---|
| `packages/workspace_service/src/workspace_service/workflow_source_execution.py` | `cb69c30708c1cd8e5db1d38312e7459fea1cefba545fbb9edff78c8b7561ea24` |
| `packages/workspace_service/src/workspace_service/workflow_mcp_execution.py` | `f4a73c8c54be7c9765115909b61eac16aa7c79f68aa6a0f9c0b768a5cae6de6b` |
| `packages/workspace_service/src/workspace_service/workflow_cad.py` | `53e1a332252dddd4bc2324b37072d4e009330f844e6dfb478df1c73f003d91e4` |
| `packages/workspace_service/src/workspace_service/workflow_application_task.py` | `5ef4fcedec06a15c4c7e19e48769e604f3d5ab6327ef9610c74484ac102f5458` |
| `packages/workspace_service/src/workspace_service/workflow_run_record.py` | `a912fef1cadca910beba466898214a7afb09c26d17d04aefa6591e53103dd34a` |
| `packages/workspace_service/src/workspace_service/workflow_design_check.py` | `599a6dc15b459b7440e4dba5fbe4a8a4f13eb6ee0f8f29e863e15d448cf05544` |
| `packages/workspace_service/src/workspace_service/workflow_async_operations.py` | `710b792f774a65edb8682bef275cc0bd2af4f2f614bf8780118a76d31fdbb6af` |
| `packages/workspace_service/src/workspace_service/workflow_resource_lease.py` | `66504607d29c5f031b0e582c79c7ca4223d7ad1d56a610d4a72ff79b8cc8185d` |
| `packages/workspace_service/tests/test_workflow_mcp_execution.py` | `5a4196b6142e494bc497c9a812a5f2294829b30ce0708a424139e599a4539d3d` |

These are untracked working-tree files, not contents attributed to the HEAD
commit. This remains a non-atomic observation during concurrent development.

**Design checks now have a bounded native path.** `compile_prompt_workflow`
recognizes `approval` connections conditioned on `pass`, and `revision`
connections conditioned on `revise`, from an MCP task explicitly configured as
a design check. `workflow_design_check.py` accepts JSON verdicts `pass`,
`revise`, or `needs_input`; checked observations cite successful tool-call
indices. One automatic rework segment is supported: a preceding create-new CAD
task using indexed files, an upstream inspection task, and an explicit limit
of one to three revisions. Other general conditional/control connections still
fail compilation. The native run invalidates affected downstream responses
between revisions. These are **agent design verdicts**, not demonstrated human
approval or evidence that every measured claim follows from the cited call.
The earlier inventory's general work-task restriction must be read with this
new exception; the old recovery contract has not changed to describe it.

**Failure handling is more explicit.** The source run recorder checkpoints
partial results, invalidates affected current results on a design revision, and
retains events and attempted revisions. History classifies a nonterminal run
using its host and application lease as running, interrupted, or unknown without
resubmission. The async-operation adapter warns that requesting cancellation
does not prove a remote mutation stopped. These are inspected paths, not newly
executed recovery/interoperability tests.

**Provider preservation gaps persist.** Fixed MCP resolution still requires
the selected installation server ID, tool name and contract digest. The CAD
adapter still chooses the non-fake `isDefault` provider from `cad.list_providers`
before pinning that choice within its task. Resource results still incorporate
local server identity and optional revisions. The draft therefore cannot infer
portable author-selected provider or resource identity from this `.wflow`
fixture alone.

### Additional Solid Edge implementation evidence

A process command line independently identified `D:/repos/SolidEdgeMCP` as a
local provider development checkout. Read-only Git inspection found origin
[`burhop/SolidEdgeMCP`](https://github.com/burhop/SolidEdgeMCP), branch
`codex/bug-fixes`, HEAD `f58a783d2bfad4cff97c818bb63d42c1485d305a`, dated
2026-08-13T17:38:10-04:00. Several tool/provider files were modified; a commit
pin alone does not reproduce the observed contracts or identify a running
binary. The origin is a repository identity observation, not registry ownership
verification or a claim of Siemens endorsement.

The project file declares `ModelContextProtocol` **1.4.0** and
`net10.0-windows`. `Program.cs` configures stdio and generates tool contracts
from the assembly, normalizes output schemas, and filters advertised/callable
tools by server mode. `SolidEdgeCadProvider.Id` is exactly `solid_edge`, with
display name `Solid Edge`. The registry also includes a separate fake provider;
omitting `providerId` resolves the server's default. The portable fixture must
therefore supply `solid_edge` explicitly and verify the intended implementation.

Current source exposes `cad.open_document`, `cad.save_document`,
`cad.list_variables`, `cad.set_variable`, `cad.rebuild_document` and
`cad.export_document`. `cad.set_variable` requires a fresh expected value, unit
and formula plus a confirmation token. This is a concrete stale-state check,
not a portable human-approval mechanism. `cad.save_document` requires an
explicit document ID and provides copy semantics; it has no active-document
fallback. The tool is specific to the Solid Edge implementation in this source.

The already hashed historical trace supplies additional **recorded**,
self-reported identity facts. Its `cad.set_variable` observation at
2026-09-07T15:45:07.2359394+00:00 reports provider version
`1.0.0+f58a783d2bfad4cff97c818bb63d42c1485d305a`, CAD product `Solid Edge` and
CAD version `226.00.01.04`. Its `cad.get_server_info` result at 15:46:17 UTC
reports name `solid-edge-mcp`, version `0.2.0`, default provider `solid_edge`,
and supported providers `fake` and `solid_edge`. These distinct version fields
are not interchangeable. The trace records that the edit's rebuild evidence is
same-session, with no close/reopen; it must not support a fresh-session claim.

No actual `tools/list` schema snapshot, negotiated protocol or compiled package
digest was captured by this refresh. The trace has Wright-local contract digests,
which do not supply the original schema bytes. A reported Git-derived provider
version also does not describe uncommitted changes in a compiled binary. The
[capture plan](../docs/wright-compatibility.md#real-solid-edge-capture-gate)
keeps these gaps explicit. No provider code or engineering models were copied.

| Provider path relative to `D:/repos/SolidEdgeMCP` | SHA-256 at refresh |
|---|---|
| `src/SolidEdgeMcpServer/Program.cs` | `06f5223c28ff03cf6fb8d23e9ea2c86f61c7aae8038142d32e5ed44aae2493fb` |
| `src/SolidEdgeMcpServer/SolidEdgeMcpServer.csproj` | `8946e7219e8c6b6e1b395427bd4efad838125873bd50c600fb968c2a9eea29ae` |
| `src/SolidEdgeMcpServer/Tools/CadTools.cs` | `0d590cbcab13484ebdb9445a2b85d2bb15fb80289a3cc095259d1bc48d927e12` |
| `src/SolidEdgeMcpServer/Tools/CadSaveTools.cs` | `4261e3bdff60259449b325008db19dd31e557a936dbe22591d3c41976fee050f` |
| `src/CadMcp.Provider.SolidEdge/SolidEdgeCadProvider.cs` | `218ab194978e30f6f1dc9bee0c7176fd341a6a5f2dbbce108eba97941f5280f3` |
| `src/CadMcp.Api/Providers/CadProviderModels.cs` | `1039eab8bdd161279f81d05ba8a7595686b8748734036fbb3d0eb81c4145323a` |
| `src/CadMcp.Core/Providers/CadProviderRegistry.cs` | `4e6f10a31625d9eacc4c6089bd7a855ff18ccd0bc117917acdaefa31c89eb2d1` |
