# Wright code review for process interchange

**Observed:** 19 October 2026. **Method:** read-only source, diff and test/evidence
inspection. Wright applications, provider operations and test suites were not
run for this documentation review. Historical passing checks below are attributed
to retained evidence, not claimed as newly reproduced results.

## Revision and local-work accounting

| Layer | Exact identity | Treatment |
|---|---|---|
| Published `dev` | `bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94` (15 October) | Isolated clean checkout; primary public implementation baseline |
| Published `main` head observed | `e2966b9991dafcd4dd198ea963677ec5ad6f81b0` | Recorded only; release availability not audited |
| Published feature head | `7e60329435cb28d8647f71477a6d7d2675e7b941`, `codex/desktop-file-download` (19 October) | Newer implementation outside `dev`; not called a released capability |
| Local integration candidate | `7a123ca5827f40de3862b63b0f3fb376a2ddd886`, `codex/desktop-integration-completion` (19 October) | Includes the feature candidate plus two local commits at observation time |
| Transient dirty integration files | Initial inventory showed runtime-lock/web-build changes; final snapshot was clean at the same commit | Initial paths/status retained; transient bytes were not captured or qualified |
| Original user checkout | `c1a8d00942d8a80ca6229ebed23d7b8f4153a7d9`, `dev` | Older than remote; three untracked workflow files inventoried, preserved and not adopted as portable examples |
| Other registered worktrees | See [inventory](local-evidence.json) | Surveyed for unpublished changes; older prototype branches do not collectively define a current runtime |

Published feature source and unpublished local work are different categories.
The local-only delta from `7e603294` comprises `bc9584aa` and `7a123ca5`:
public sign-in metadata/scanner corrections, associated qualification evidence and
history-scan confinement. It does not introduce a new bundle/interaction version.
The local sign-in constructor name changes to `remote_signin_mode` while retaining
the public runtime metadata key `remote_oauth_flow`.

The main integration checkout showed seven generated build/lock status entries
during the initial survey, then was clean at the same commit by the content-hash
snapshot. This review did not change those files; their transient bytes were not
captured and no build claim is made. Other dirty legacy worktrees contain planning
or earlier editor/prototype work.
One historical trace checkout has thousands of missing tracked files; it was
inventoried as incomplete, not interpreted as a deliberate product-wide deletion.
No checkout was reset, rebased, cleaned or otherwise repaired by this review.

The evidence file records relative repository paths, source hashes, local heads
and status counts. It deliberately does not copy private workflow contents,
credentials, installed state or large generated builds. Local-only commits have
no invented GitHub source links; public links use the last published revision.

## Findings and consequences

| Finding from implementation | Consequence for the shared specification |
|---|---|
| A source/bundle export and inspect/import owner now exists | Document the real envelope and lifecycle, instead of treating packaging as wholly future work |
| Imports compare derived source dependencies with manifests and keep `can_run: false` | Integrity/import, language support and execution readiness need separate claims |
| Instructions and typed assumption policy are embedded in accepted source | Behavior text and explicit policy are portable dependencies, not recipient defaults |
| V1/V2/V3 human-input declarations exist | Preserve deliberate waits and conditional ask/skip semantics; do not infer arbitrary branching |
| Validation uses exact subject/profile/baseline identities | Preserve acceptance criteria, measurements and invalidation; tool success is insufficient |
| Imported UI is inactive and version-bound | Transfer editable presentation separately from local build trust and run authority |
| Import reservation precedes assets; source publication comes last | Preserve uncertainty and prohibit replay after partial or unacknowledged writes |
| Provider requirements still contain local IDs and schema pins | Portable identity/rebinding remains an interoperability gap, not a solved registry problem |
| Desktop and web transports share owners and runtime | Host integration demonstrates reusable presentation, not an independent executor |
| Local/feature deterministic execution avoids unnecessary reasoning callbacks | A portable deterministic process must not be forced to acquire an AI dependency |

## Newer feature and local candidate inspection

The following implementation was inspected in the local integration candidate and
is already present in published feature head `7e603294`, but not in the pinned
`dev` baseline. The public links identify that feature version; the evidence file
also hashes the inspected local bytes.

- **Deterministic tool-only work:** `step_requires_model` is shared by model
  freezing/restoration and dispatch. The runtime resolves reasoning callbacks only
  if a step actually needs a model. Two focused regression tests cover no-model
  execution and retaining the model factory requirement for AI work.
  [Routing](https://github.com/burhop/wright/blob/7e60329435cb28d8647f71477a6d7d2675e7b941/packages/workspace_service/src/workspace_service/workflow_model_routing.py),
  [execution](https://github.com/burhop/wright/blob/7e60329435cb28d8647f71477a6d7d2675e7b941/packages/workspace_service/src/workspace_service/workflow_source_execution.py),
  [tests](https://github.com/burhop/wright/blob/7e60329435cb28d8647f71477a6d7d2675e7b941/packages/workspace_service/tests/test_workflow_mcp_execution.py).
- **Recoverable editor drafts:** the source owner stores
  `wright.workflow-editor-draft/1` with source, applied source, layout/view,
  accepted base and compare-and-set identity. Restoring an inert draft is separate
  from accepting it or running it. Draft storage is local editing state, absent
  from the transfer bundle.
  [Owner](https://github.com/burhop/wright/blob/7e60329435cb28d8647f71477a6d7d2675e7b941/packages/workspace_service/src/workspace_service/workflow_sources.py),
  [tests](https://github.com/burhop/wright/blob/7e60329435cb28d8647f71477a6d7d2675e7b941/packages/workspace_service/tests/test_workflow_editor_drafts.py).
- **Historical evidence after source edits:** the native panel can inspect the
  exact saved run's evidence rather than treating the currently open source as
  authority for that old run. This supports preserving history without reviving
  stale approval or dispatch authority.
  [View](https://github.com/burhop/wright/blob/7e60329435cb28d8647f71477a6d7d2675e7b941/apps/web/src/prototypes/desktop-panel/NativeRunEvidence.tsx).
- **Provider setup and replacement:** local controls reuse existing onboarding,
  credential and permission owners. Replacement starts from a reviewed public
  template and creates a separate provider; old keys/grants/workflow bindings are
  not silently migrated. Private authentication/configuration remains outside a
  shared process file.
  [Replacement template](https://github.com/burhop/wright/blob/7e60329435cb28d8647f71477a6d7d2675e7b941/prototypes/desktop-harness/desktop_connection_template.py),
  [backend](https://github.com/burhop/wright/blob/7e60329435cb28d8647f71477a6d7d2675e7b941/prototypes/desktop-harness/desktop_backend.py).
- **Qualification limits:** retained evidence distinguishes protocol/browser/GB10
  checks from actual Windows host acceptance, personal login completion, model
  identity and generated-UI capability. No new native-host or engineering
  acceptance is inferred here.
  [Dated checkpoint](https://github.com/burhop/wright/blob/7e60329435cb28d8647f71477a6d7d2675e7b941/prototypes/desktop-harness/integration-status-20261019.md).

## Uncommitted prototype source

The older `codex/openai-desktop-harness-prototype` worktree at `c0769319` still
contains uncommitted editor changes and an untracked reasoning-status reader/hook.
The inspected reader uses a read-only request, checks workspace/session/run and
request identities, and labels a pending desktop conversation task without
answering it or executing tools. The editor only connects that presentation to
the matching source/run. This reinforces P16's separation of presentation from
execution authority; it is not a new transfer dialect or an additional executor.
Comparable reasoning-status files already exist in the published development
baseline, so an old dirty prototype is not automatically a newly unimplemented
feature. Four inspected working-file hashes and comparison identities are recorded
in [local evidence](local-evidence.json). Their contents are not copied here.

## Evidence by claim

| Claim inspected | Primary source/test | What it does not prove |
|---|---|---|
| Definition-only bundle and integrity bounds | [Core model](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/src/core/workflow_bundle.py), [core tests](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/tests/test_workflow_bundle.py) | Independent parser compatibility |
| Cross-workspace source/instruction/asset/profile/UI handling | [Owner tests](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/tests/test_workflow_bundles.py), [retained proof](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/specs/083-process-working-interfaces/evidence/workflow-bundle-transfer.md) | Independent executor or arbitrary extension preservation |
| Real native transfer and lost-reply reconciliation | [Transfer checkpoint](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/prototypes/desktop-harness/workflow-transfer-plan.md), [probe](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/prototypes/desktop-harness/workflow_asset_transfer_probe.py) | Windows delivery, engineering output or complete saved-UI host parity |
| Conditional declared inputs | [Source compiler](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/src/workspace_service/workflow_human_input.py), [tests](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/workspace_service/tests/test_process_conditional_human_input.py) | Arbitrary dynamic forms or general graph conditions |
| Validation identity and gating | [Contracts](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/packages/core/src/core/process_validation.py), [source contract](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/specs/082-output-content-validation/contracts/process-source.md) | Physical verification or human acceptance |
| Shared UI and durable interaction | [Interaction contract](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/specs/083-process-working-interfaces/contracts/process-interaction.md), [UI contract](https://github.com/burhop/wright/blob/bcb5b52f1f7169eb0b5b71bc1a1ef704b6911a94/specs/083-process-working-interfaces/contracts/ui-authoring-and-hosting.md) | A universally supported host/client protocol |

Several Wright design documents intentionally retain dated historical gaps and
checkpoints. Current implementation findings above come from the pinned code and
its corresponding tests; old “planned” paragraphs do not override implemented
source, and checked tasks do not substitute for observed execution evidence.

## Remaining work before cross-tool claims

1. Specify portable provider/resource identity and reviewed local rebinding without
   treating a matching tool name/schema as provider equivalence.
2. Define a small executable subset and publish independent parser/hash vectors;
   identify opaque extension and lossless round-trip rules.
3. Qualify declaration completeness for referenced files/provider resources and
   clarify model substitution when an export requests `workspace-default`.
4. Run the selected engineering cases in a genuinely separate implementation,
   retaining exact input/output/check evidence and unavailable-provider controls.
5. Keep source, transport, runtime, engineering, host UI and user acceptance claims
   distinct. Licensing/governance and standards selection remain separate decisions.
