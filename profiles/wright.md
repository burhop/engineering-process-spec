# Wright implementation profile — October 2026

**Status:** descriptive implementation snapshot, not a stable interchange standard.
Published `dev` baseline: `bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94`.
Feature/local differences are isolated in the [code review](../research/wright-code-review.md).
Wright remains the authority for this dialect; this document does not replace its parser.

## 1. Source, authoring and execution are different boundaries

The visible accepted definition is `workflows/<safe-slug>.workflow.wflow`.
Source storage preserves UTF-8 bytes, uses host-assigned revisions and
compare-and-set digests, and stores layout separately. A raw source save is not
proof of compiler acceptance or readiness. Ordinary creation may materialize
instruction defaults; export uses the exact subsequently accepted bytes.

The editor's canonical model, command protocol and source projection are not
interchangeable with the runtime compiler's supported subset. The compiler admits
`workflow`, `task`, `input`, `connection`, `group` and `item` sections; it requires
one connected process and 1–32 tasks. It orders supported dependencies and executes
the resulting steps through the existing source runtime. General conditional
edges and arbitrary cycles are rejected. Supported design-check pass/revision
edges and validator-owned bounded rework are specific mechanisms, not a promise
of arbitrary loops, parallel execution or BPMN semantics.

Supported step forms include AI work, exact MCP calls, scoped MCP agent work,
validation, declared input and review/action barriers. Availability is checked by
the owning compiler/preparation services. The legacy canonical schemas under
Features 078–080 remain useful historical contracts, but are not a complete schema
for all current instructions, source extensions or runtime behavior.

Sources: [compiler](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/workflow_source_execution.py),
[source owner](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/workflow_sources.py),
[historical kernel contract](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/specs/080-canonical-workflow-recovery/contracts/conformance-kernel.md).

## 2. The actual transfer envelope

`wright.workflow-bundle/1` is a **JSON object**, not a ZIP archive. Both modes
use the same envelope. A source-mode export is not just a bare `.wflow` file.

| Field | Meaning at this revision |
|---|---|
| `schema_version` | Exactly `wright.workflow-bundle/1` |
| `mode` | `source` or `bundle` |
| `source`, `source_digest` | Accepted source string and SHA-256 of its exact UTF-8 bytes |
| `layout` | Optional validated diagram layout; not execution state |
| `assets` | Declared files with relative `path`, `sha256`, `data_base64` |
| `dependencies` | `category`, `identity`, `disposition`, optional `sha256`, typed-by-category `details` checked by the service |
| `interfaces` | Optional manifest, editable source envelope and source digest; no trusted build |

Dependency categories are `reference`, `validation_profile`, `provider`, `model`,
`instructions` and `ui`; disposition is `embedded` or `external`.
Source mode forbids assets and interface source but retains the dependency inventory.
Bundle mode can carry selected declared references, validation dependencies and
selected saved UI source. A manifest is not trusted merely because it parses:
the service derives required dependencies from the source and compares them.

Implementation bounds: 1 MiB source, 8 MiB per file asset, 64 file assets,
256 dependencies, 16 interfaces and 20 MiB canonical serialized bundle. Interface
source has additional own limits. Paths are bounded relative paths with reserved,
hidden, traversal, duplicate/case-alias and file/directory-conflict restrictions.
These are Wright profile limits, not proposed universal limits.

The export service returns `{bundle, bundle_digest}`; the shared file parser accepts
that wrapper or the bundle object. Source/file digests hash exact bytes. Structured
digests use Wright's Python `canonical_json`: sorted keys, compact separators,
UTF-8, non-ASCII characters unescaped and finite JSON numbers. Do not substitute
another JSON canonicalization or assume JavaScript number rendering is identical.
Cross-language vectors for this bundle profile are still needed.

Sources: [bundle models](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/src/core/workflow_bundle.py),
[canonicalization](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/src/core/process_validation.py),
[bundle service](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/workflow_bundles.py),
[shared client](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/apps/web/src/services/workflow-bundles.ts).

## 3. Export, inspect, import, then prepare

In the existing workflow editor use **Export / import workflow** on the saved
process. Select source mode or a bundle of declared references/UI source. In the
receiving workspace inspect the file, choose a fresh destination, import, then
configure dependencies and prepare a new run. Readiness and review remain separate.
The desktop prototype routes the shared dialog to the same owners; it is not a
second executor. Host file delivery must be qualified separately.

The authenticated HTTP owner exposes POST operations under
`/api/workspace/workflow-bundles/`:

| Operation | Important request fields | Outcome |
|---|---|---|
| `export` | `session_id`, `path`, `expected_storage_digest`, `mode`, `selected_reference_paths`, `selected_ui_ids` | Exact-source bundle and digest |
| `inspect` | `session_id`, `bundle`, `destination_path` | `bundle_digest`, `can_import`, **`can_run: false`**, diagnostics, requirements and external dependencies |
| `import` | Above plus `expected_bundle_digest` | New local source document, imported paths and inspection |

The source/dependency parser used for inspection is not the full execution
compiler. `can_import: true` only permits definition import. Missing external
capabilities can produce warnings; corrupted or inconsistent embedded dependencies
block it. Provider/model requirements always need local qualification. Typical
codes are `bundle_import_invalid`, `external_dependency`,
`local_qualification_required`, `profile_installation_required`,
`ui_rebuild_required` and `ui_version_incompatible`.

Import does not overwrite destination source/assets. It reserves
`imported-assets/<destination-slug>/manifest.json` **before** publishing assets,
then writes the new source last. The reservation survives a partial failure and
blocks replay at that destination. This is not a multi-file atomic transaction
or proof of completion; retained partial files require reconciliation. Imported
instructions bypass new-draft defaults. Local storage/revision identity is new.

Sources: [routes](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/apps/api/src/api/routers/workflow_bundles.py),
[owner](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/workflow_bundles.py),
[tests](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/tests/test_workflow_bundles.py),
[desktop transfer evidence](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/prototypes/desktop-harness/workflow-transfer-plan.md).
The transfer evidence contains dated checkpoints; its original “not integrated”
opening is historical relative to this pinned merged `dev` revision.

## 4. Instructions and model requirements

`wright.workflow-instructions/1` contains embedded assets, ordered role bindings,
policy and explicit layers. Each `wright.instruction-asset/1` has an ID, role,
version, body, body digest, origin, variables and execution-contract version.
Bindings cannot refer to absent bodies or cross role scopes. Overrides explicitly
append or replace. `document_reasonable` and `require_specified` are typed policies;
protected requirements remain distinct. Optional `wright.workflow-action-intent/1`
metadata is preserved without changing older shapes when absent.

New-draft defaults are captured at authoring; accepted source retains its own
instructions until an explicit revision. A legacy source without instructions
exports an external `legacy-local-defaults` dependency and migration requirement.
Export does not silently modernize it.

Model dependencies can still say `workspace-default`. Therefore instruction
portability does **not** freeze the author's actual model across installations.
The runtime separately resolves/freezes available model/adapter configuration and
checks continuation. Requested, confirmed and upstream-reported identities differ;
the desktop harness can explicitly report model identity as unknown. Actual
request evidence is bounded by observable/redacted transport boundaries.

Sources: [instruction models](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/src/core/workflow_instructions.py),
[settings/source materialization](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/workflow_instruction_settings.py),
[routing](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/workflow_model_routing.py),
[desktop reasoning](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/src/core/desktop_reasoning.py).

## 5. Human input, validation and external actions

Preparation classifies dependencies as `supplied`, `explicit_default`,
`upstream_produced`, `declared_human_response` or `unresolved`. Input snapshots
bind the exact process and values; answers do not rewrite the reusable definition.

Human input declarations have versions **1, 2 and 3**. V1 requires connected
producer evidence. V2 also permits an initial question. V3 adds an explicit
`unresolved_fields` condition over a connected structured requirements result;
the response fields remain fixed and closed. The runtime records ask/skip evidence.
This is not arbitrary conditional graph execution or an AI-generated form.
A waiting answer is schema/subject bound and resumes the same run. Input responses
are not engineering approvals. Rework across answered checkpoints is constrained.

`wright.process-validation/1` binds profiles/baselines, exact subjects, producers,
measurements and findings. Required checks, missing evidence, stale output and
bounded correction remain the validator/runtime's responsibility. External-action
reviews bind their own exact subject; a recorded decision is separate from current
readiness to continue and dispatch. Receipts and observations do not establish
unobserved completion or make uncertain effects safe to replay.

Sources: [input compiler](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/workflow_human_input.py),
[conditions](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/src/core/workflow_input_conditions.py),
[validation](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/src/core/process_validation.py),
[runtime/source contracts](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/specs/083-process-working-interfaces/contracts/runtime-and-source.md).

## 6. Optional working interfaces and host independence

`wright.process-interaction/1` exposes context, readiness, inputs, outputs,
assessments, pending interactions, observations and permitted actions.
Mutation actions require exact subject identities. Common and tailored views
consume those same backend facts alongside the existing diagram/source editor.

`wright.process-ui/1` manifests carry UI/revision identity, process binding,
interaction/client/kit versions, selectors and requested capabilities. The reviewed
importer recognizes client/kit `1.0.0`; incompatible versions warn and retain
common-view fallback. Imported UI source is an inactive candidate requiring local
rebinding, rebuilding and review. Its old process/workspace identifiers provide
binding context, never authority in the receiver.

MCP App hosting and WebMCP are not a general portable process client. Wright's
native desktop frontend and Hermes frontend reuse Wright runtime services.
Desktop conversation reasoning is an adapter to that runner, not evidence of
independent process execution. Generated UI authoring remains unavailable where
a host cannot satisfy the confined authoring contract.

Sources: [interaction models](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/src/core/process_interactions.py),
[UI models](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/src/core/process_interfaces.py),
[UI contract](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/specs/083-process-working-interfaces/contracts/ui-authoring-and-hosting.md).

## 7. Portability limits that must remain visible

- Provider declarations preserve local `server_id`, tool and schema requirements,
  but do not yet provide a complete implementation-neutral provider identity and
  rebinding protocol. Import explicitly requires local registry review.
- Reference discovery is declaration based, including `workspace_file` inputs
  and known validation/UI dependencies. It is not a general scanner for files,
  absolute paths or provider resources mentioned inside prompts/tool arguments.
- Missing providers can be retained as definition dependencies. Unknown syntax or
  required fields can still be rejected; arbitrary opaque-extension editor
  round-tripping is not established.
- Schema validation and transport success do not prove engineering equivalence.
  Identical MCP operation schemas can hide different provider behavior.
- Credential-field/path checks are bounded safeguards, not proof that arbitrary
  prose or file bytes contain no sensitive information. Exported content still
  needs appropriate selection; a digest proves identity, not confidentiality.
- Cross-workspace Wright transfer, mocked tests and another Wright frontend do
  not prove independent-executor interoperability. No such proof was found in
  this review, and no engineering runs were started for it.
