# Engineering process interchange — draft requirements

**Status:** proposed, 19 October 2026. This is a semantic requirements draft,
not a new executable grammar or a ratified standard. MUST, MUST NOT and SHOULD
express the proposed obligations of a conforming implementation. The
[Wright profile](../profiles/wright.md) records current implementation separately.

## 1. Scope and participants

An author creates an engineering process. A reader inspects it, an editor changes
it, and an executor performs its declared work using available capabilities.
One application may implement several roles. A process UI presents inputs,
results, decisions and progress for that executor's run.

The interchange unit is a **reusable definition and its declared dependencies**.
It is not a running job, an authorization token or an installation image. Moving
an active run between executors requires a separate future protocol.

No mandatory CAD/manufacturing lifecycle or screen layout is prescribed. A
process may calculate, design, analyse, inspect, compare, document or request an
external operation. Supported graph semantics must be explicitly identified.

## 2. Information that must survive exchange

| Subject | Proposed preservation requirement |
|---|---|
| Definition | Source dialect/version, process and block identities, typed ports, dependencies, supported control semantics and applicable instructions |
| Inputs | Value/schema, units and reference frame where applicable, requirements, explicit defaults, declared source of later values and file/resource identities |
| Operations | Chosen provider/application, operation, configuration, compatible contract/version requirements and parameter mappings |
| Outputs | Expected representations, producer/port associations and downstream consumers |
| Acceptance | Required checks, criteria, units/tolerances, profile/baseline references, evidence requirements and human review declarations |
| AI behavior | Actual instruction bodies/templates, ordered bindings, versions/digests, explicit policy and model/adapter requirements |
| Human interaction | Declared question or decision kind, response schema, evidence subject, condition if supported and continuation semantics |
| Recovery | Declared retry/rework limits, scope, invalidation and uncertain-outcome handling |
| Dependencies | Embedded versus external disposition, identity, integrity and compatibility requirements |
| Optional presentation | Layout or UI source/bindings, required contract/client/kit versions and fallback expectations |

A global prompt profile name, local server UUID or filename alone does not prove
that the receiving system has the same instructions, provider or engineering data.

## 3. Preservation, interpretation and compatibility

**P01 — Faithful transfer.** A reader/editor MUST preserve the meaning of accepted
source and required dependencies. An editor MUST NOT silently drop unavailable
blocks or replace a specific tool with a generic capability. Byte-preserving
round trips and semantic-equivalence round trips are different claims.

**P02 — Versioned interpretation.** A package MUST identify the dialect and required
contracts it uses. An implementation MUST state its supported subset. Unknown
required semantics MUST block execution. An application MAY retain an unsupported
package opaquely for inspection/export; that does not count as understanding it.

**P03 — Deliberate changes.** Provider replacement, changed instructions, relaxed
checks and changed interaction semantics MUST be visible definition edits. Any
claimed conversion MUST disclose unsupported or lossy mappings. A new local
revision MUST NOT inherit old review authority.

**P04 — Integrity and identity.** The applicable profile MUST define exact byte
hashing, structured canonicalization and revision rules. Definition identity,
local storage identity, run identity, artifact identity and UI identity MUST remain
distinct. Presentation-only edits SHOULD NOT invalidate engineering work unless
they change process semantics. Cross-language digest equivalence needs test vectors.

## 4. Dependencies and local readiness

**P05 — Specific providers.** Exchange MUST preserve the intended provider and
operation, not merely a similarly named tool or matching parameter schema.
Receiving applications bind that requirement to local installations/connections.
Matching names, UUIDs or schema hashes alone MUST NOT establish semantic equivalence.
The portable provider-identity/version representation remains an open design item.

**P06 — Separate checks.** An implementation MUST distinguish:

1. Package integrity and supported structure.
2. Semantic validity within an identified dialect/subset.
3. Dependency availability and local execution readiness.
4. Execution outcome and engineering acceptance.

A successful import MUST NOT imply the other stages passed. Diagnostics SHOULD
identify the affected dependency/block, reason and correction without exposing
credentials. Missing support MUST remain explicit rather than trigger substitution.

**P07 — Input responsibility.** Before start, each required input MUST be supplied,
explicitly defaulted, produced by declared upstream work, or assigned to a declared
human-input step. Intermediate outputs need not exist before their producers run.
Static readiness cannot establish that arbitrary prose has captured every
engineering requirement. External conditions MUST be rechecked when needed.

**P08 — Dependency completeness.** Required instruction/reference/validation/UI
assets MUST be embedded or explicitly external. Importers MUST verify their
identities and independently validate the inventory against understood source.
They MUST reject corruption or undisclosed required dependencies within that
supported subset. How opaque extensions declare their dependency closure is unresolved.

Credentials, installed programs and environment-specific connectivity are local
responsibilities. Neither a reachable service nor an installed MCP server proves
access to the intended resource or permission to perform the operation.

## 5. Instructions and execution

**P09 — Inspectable behavior.** Accepted AI instructions MUST travel with the
process, including applicable helper/recovery templates and ordered overrides.
Changing the receiver's defaults MUST NOT silently change an imported definition.
Typed policy controls behavior; prose MUST NOT grant permissions or replace
validation. Declared assumptions MUST remain distinct from supplied requirements
and measured facts. AI output need not be bit-for-bit reproducible.

**P10 — Resolved execution configuration.** An executor MUST record the actual
resolved source, inputs, tools and any model/adapter configuration used by a run,
and check their continued compatibility on resume. Requested aliases, observed
routing and a reported upstream model revision MUST be distinguishable. An
unreported model identity MUST remain unreported. A deterministic tool-only
process MUST NOT acquire an unnecessary AI dependency from its presentation host.

**P11 — Declared interaction.** Human input, engineering review and permission for
an external action MUST be distinct. A declared wait MUST have a durable subject
and a validated response that continues the same run. Invalid/stale responses
MUST NOT advance it. Unattended steps MUST NOT invent questions outside their
accepted interaction policy. A conditional question requires explicit supported
condition semantics and retained evaluation evidence.

## 6. Engineering results, reviews and recovery

**P12 — Exact evidence.** Checks MUST refer to the exact output/resource revision,
producer and applicable criteria/baseline. Evidence SHOULD record method, source,
units, tolerances and limitations. Tool success, artifact existence, measured
compliance, human acceptance and physical verification MUST remain separate facts.
An unavailable mandatory check MUST hold the dependent action, not lower its bar.

**P13 — Invalidation.** Changes to bound inputs, assumptions, source, profiles,
provider contracts or output revisions MUST invalidate the affected downstream
claims and decisions. Unaffected work SHOULD be retained where dependencies prove
it remains valid. Do not claim arbitrary incremental recomputation without support.

**P14 — Bounded recovery.** An executor MUST honor declared correction limits and
preserve prior failed outputs/findings. Rework MUST NOT silently cross an answered
human checkpoint, change the assignment or bypass a mandatory review. Arbitrary
cycles, parallelism and compensation are not implied by this draft.

**P15 — External effects.** An external operation MUST retain exact inputs,
destination, authority, attempt identity and available receipts/observations.
Submission, acceptance, observed activity and completion are separate facts.
An unknown outcome MUST require reconciliation, not automatic replay. Cancelling
a request MUST NOT be represented as proof that a physical operation stopped.

## 7. Optional process interfaces

**P16 — One execution authority.** Authoring/inspection and a common or tailored
working UI MUST use the same accepted process and durable run. A working UI
consumes explicit inputs, evidence, pending interactions, observed state and
permitted actions for exact subjects. It MUST NOT introduce a second executor,
vendor protocol implementation or independent completion authority.

**P17 — Compatibility and fallback.** Reusable UI assets MUST declare process
bindings and supported interaction/client/kit versions. Imported code MUST remain
inactive until the receiver's local compatibility/build/review policy is met.
An unavailable UI SHOULD leave a usable common view. Closing/reopening a view
MUST reconcile with durable state without resubmitting uncertain effects.
A particular UI framework, desktop host or tab layout is not part of the core
interchange contract. Wright's workspace tabs are its implementation choice.

## 8. Authority and import recovery

**P18 — Definition-only transfer.** A definition package MUST NOT transfer
credentials, active sessions/runs, prior answers, permissions, approvals or trusted
UI builds. Historical evidence may be shared by a separately scoped mechanism,
but MUST NOT become authority for a new run. Defaults intentionally authored in
a definition are distinct from private answers collected in an earlier run.

**P19 — Non-destructive import.** Import MUST use an explicit destination and
integrity-checked package identity, preserve existing work, and provide actionable
diagnostics. Lost acknowledgements or partial writes MUST have a read/reconciliation
path. A reservation or manifest MUST NOT be presented as proof of completion.
Automatic replay after uncertain publication is prohibited.

## 9. What this draft does not standardize yet

The final syntax/container, provider identity registry, version negotiation,
opaque-extension preservation, unit vocabulary, cross-language canonicalization,
independent execution subset and optional runtime/result protocol remain open.
No BPMN/CWL/SysML/MCP profile has been selected by this update. MCP connectivity
is a tool boundary, not by itself a definition language or an independent executor.
See the [research agenda](../RESEARCH.md) and [conformance plan](../conformance/README.md).
