# Proposal 001: first exchange and execution boundary

Status: **proposed for owner review**, 2026-09-07. This is a research conclusion,
not an accepted specification, compatibility promise or stable standard.
No Wright implementation change, repository visibility change, license choice
or external publication is authorized or performed by this document.

## Recommended decision

Build a small **engineering process exchange and provider-binding profile**.
Use an existing workflow representation for executable behavior; add only the
identity, preservation, resource and evidence rules needed for faithful exchange.
Do not introduce a new grammar or copy all of Wright's evolving canonical model.

Use **Open Workflow Specification 1.0.3 as the first experimental executable
candidate**, with fixed MCP calls and an explicitly pinned `2025-11-25` protocol
binding to match inspected Wright source. Trial **RO-Crate 1.2** for packaging.
These are provisional technical choices. Adoption requires two independent
implementations passing the bounded profile, including unavailable-provider
tests. The OWS document/schema discrepancy and newer MCP lifecycle must be
resolved explicitly; a latest-version label is insufficient.

Keep **CWL 1.2.1** as the calculation baseline and practical fallback if the OWS
MCP experiment needs excessive custom execution work. Use **BPMN 2.0.2/DMN 1.5**
to evaluate the subsequent human-approval profile. Do not require all three
workflow languages in the first specification. These choices follow the
[comparison](../research/comparison.md),
[implementation findings](../research/findings.md#2-process-candidates-go-deepest-on-execution-and-binding)
and [MCP evidence](../research/findings.md#3-mcp-explicitly-a-protocol-with-several-identities-and-versions).

## First specification boundary

The first claim should be precise: an independent application can read and
preserve a package, identify the intended provider/resources, and execute its
supported fixed-call subset when those prerequisites are available. When they
are unavailable, the same process remains intact and the reason is observable.

| Included in the first proposed profile | Boundary and rationale |
|---|---|
| Package and authority | One authoritative workflow entrypoint; source language/profile versions; artifact identities and required external references. Original Wright source is a separately identified source artifact, not a second editable authority |
| Supported execution subset | Fixed named MCP calls, explicit input/output handoff, bounded failure paths and a small deterministic calculation. Choose exact allowed constructs after the engine experiment |
| Intended provider binding | Publisher/implementation identity, application provider inside the server, tool/protocol contract and declared compatibility. Keep receiving endpoints, local UUIDs and credentials separate |
| Resource handoff | Input file identity or provider-scoped resource/revision; output representation, provenance and durability. Require evidence that the downstream step receives the intended model |
| Preservation and diagnostics | No-op preservation, unknown-required-feature handling, invalid versus unavailable distinctions and no implicit substitution |
| Outcomes | Execution state, trustworthy partial outputs, measured acceptance and references to approval evidence as separate concepts |

The initial artifact is still a **profile of the chosen workflow language**.
Package metadata can associate a workflow node with provider/resource
requirements using explicit references, without duplicating its task graph.
If those references become stale after an edit, validation fails. A conforming
executor must understand this required profile before executing the workflow;
an ordinary engine that ignores it cannot claim our execution conformance.
Exact extension/reference encoding remains an experiment, not a schema invented
in this research.

Defer unrestricted AI task execution, general CAD-provider equivalence,
automatic conversion between workflow languages, full human-approval execution,
distributed compensation, resumable state migration, broad version ranges and
semantic hashing. Preserve unsupported original definitions as unsupported
source; do not label archival preservation as independent execution.

The existing Wright CAD fixture is AI-driven and uses installation-specific
identity. A new fixed-call process must be authored explicitly from verified
tool contracts. It is not automatically equivalent to that fixture. Wright's
current contracts, native compiler and recorded evidence remain separately
identified in [the inspection](../research/wright.md).

## Adopt, reference, extend or define

| Action | Recommendation | Tradeoff |
|---|---|---|
| Adopt existing syntax, conditionally | OWS fixed-call experiment; CWL calculation comparison; JSON Schema 2020-12 for structural additions | Reuses tooling but inherits version/extension inconsistencies and requires profile-aware adapters |
| Adopt protocol deliberately | MCP with exact protocol revisions and tested capabilities; preserve protocol and tool error causes | Connects real tools but does not supply process, application identity or engineering acceptance |
| Trial packaging | RO-Crate 1.2, one entrypoint, immutable payload identities and explicit external references | Reuses descriptive packaging; adds JSON-LD/profile tooling and still needs an execution contract |
| Reference engineering standards | STEP/QIF artifact profiles, UCUM units, SysML/KerML engineering concepts; ISA-95/AutomationML when cases need them | Avoids parallel domain vocabularies; detailed ISO/IEC conformance needs material not fully accessed here |
| Extend upstream where appropriate | Clarify OWS MCP version rules and add protocol-specific provider/failure test examples; use existing namespace/extension mechanisms | Benefits other implementers, but upstream acceptance and timing are unknown |
| Define the missing exchange rules | Intended-versus-local identity, preservation of unavailable/unknown blocks, binding evidence, resource lifetime/revision and separate outcome/acceptance/approval | Small new semantic surface is unavoidable; keep it testable and independent of Wright |

RO-Crate is optional at the experiment stage: if two independent readers need
disproportionate machinery for this small package, compare its minimum useful
profile with a simple manifest plus existing metadata. Record the measured
cost and lost reuse before choosing; do not silently create a second packaging
standard because JSON-LD is unfamiliar.

## Author choice and application responsibilities

The Solid Edge MCP block stays a Solid Edge MCP block. A receiving application
may configure a different endpoint for the **same intended provider** after
checking identity/compatibility and resource access. That is local rebinding.
Selecting another provider or changing the operation/representation contract is
an explicit process edit with a new revision, checked connections and reassessed
downstream acceptance. Matching tool names, schemas or capabilities do not
authorize replacement.

The package retains requirements. The application checks availability, explains
the relevant block/dependency, gates execution and supports configuration or
user-directed replacement. A Linux authoring client with access to a compatible
remote provider can be usable; one with no such access preserves the definition
and reports unavailable execution. This remains distinct from an unknown
required language feature, for which interpretation itself is unsupported.

## Evidence gate and alternatives

Require an independent reader/resolver, plus two independently implemented
executors/adapters for the selected bounded profile. Report shared libraries.
Two AI models using Wright's executor do not satisfy this gate. A fake MCP
service demonstrates resolver/error behavior; only real named-provider runs
demonstrate the CAD part. The complete proposed cases and 19 tests are in
[interoperability.md](../use-cases/interoperability.md).

| Alternative | When it would be preferable | What it would cost |
|---|---|---|
| Package-only first release | Immediate archival exchange is the sole milestone | Does not meet independent understanding/execution of the process; can be a preliminary reader milestone only |
| CWL-first executable profile | Batch calculations and command wrappers dominate, with manageable explicit MCP adapter requirements | Stateful application handoff and human workflow need additional contracts |
| BPMN-first profile | Durable human approval/control is essential in the first release | Must standardize executable service bindings and test vendor extensions, beyond diagram interchange |
| Full SysML/KerML foundation | Rich engineering model semantics are the central authoring requirement | Much larger implementer burden; still needs actual tool execution bindings |
| Export Wright's full current grammar/IR | Exact Wright features are the overriding immediate requirement | Makes an evolving implementation contract the ecosystem's new language; currently has divergent source/canonical/native paths |

The recommended OWS experiment wins on explicit MCP-call representation, not on
demonstrated complete conformance. If it requires a new bespoke interpreter or
cannot preserve mandatory identity constraints across engines, fail the gate
and select the bounded CWL alternative or revise scope. Do not declare success
by weakening the author-choice invariant.

## Prioritized next-step plan

1. **Agree the experimental boundary and capture a reproducible fixture.** Keep
   the profile proposed. Record actual Solid Edge server/publisher/application
   identities, exact MCP schemas and revisions, allowed execution target, model
   bytes and expected measurements. Resolve sample-distribution rights before
   publishing it. Author the fixed-call variant explicitly. Exit: no invented
   provider pins, one authority, complete input/acceptance inventory.
2. **Prove preservation and binding before CAD execution.** Implement an
   independent reader/resolver from the proposed contract. Use fake providers
   to test missing tools, changed defaults, same names on different servers,
   unsupported profiles and no-op saves. Exit: P01–P04 and B01–B06 pass with
   machine-readable evidence; no Wright parser dependency.
3. **Select the executable representation using working implementations.** Pin
   OWS runtime/SDK/schema/CTK revisions and attempt the fixed MCP profile with
   separately implemented bindings. Run the calculation/error cases and compare
   CWL's adapter burden. Resolve OWS schema/reference ambiguity and specify
   `isError` handling. Exit: two independent executions, documented supported
   subset, actual implementation effort and known gaps; select one baseline.
4. **Run real CAD transfer and recovery cases.** On prepared installations,
   execute the same declared Solid Edge process, then repeat with the intended
   provider unavailable and with controlled partial failure. Verify input
   preservation, final readback and artifact evidence. Exit: E02/E04/E05 and
   replacement behavior pass; claims remain limited to measured properties.
5. **Publish an implementer kit when publication and terms are settled.** Keep
   the specification, schemas, fixtures and expected results versioned together;
   keep the independent test harness usable without Wright. Provide a short
   quickstart, invalid/unavailable examples, diagnostics guide, binding guide,
   extension rules and per-implementation conformance matrix. Exit: a new
   implementer reproduces the supported cases from the documentation.
6. **Expand with evidence and appropriate governance.** Add inspection/approval
   only after its identity, authorization and stale-result tests are specified.
   Invite independent implementation review once contribution terms are agreed;
   use a small working group and shared test rounds. Consider foundation or
   formal standardization only with sustained participation and interoperability.
   Exit: accepted scope and governance based on real contributors and results,
   before any stable 1.0 claim.

Implementation experiments are future work. Wright continues to own its
evolving implementation; independent prototypes and portable test ownership
must be agreed at the experiment stage. This repository currently contains
research and proposed contracts only.

## Unresolved decisions

- **Baseline and versions:** do two OWS implementations support the required
  fixed-call/MCP subset, and which exact releases? When should the 2026 MCP
  lifecycle become a separately tested binding? No compatibility is inferred.
- **Provider identity and compatibility:** which publisher-controlled identifier
  anchors the actual Solid Edge MCP; how are application identity, tested
  updates, multi-provider servers and non-SemVer builds handled? What installed
  package or authenticated-service evidence supports self-reported identity?
- **Package/extension encoding:** minimum RO-Crate profile, required-extension
  mechanism, node references, unknown-content editing, archive format and
  authoritative-source mapping. No semantic canonicalization is selected.
- **Resource and engineering contracts:** required revision evidence for native
  or cloud objects; tolerances, unit-conversion scope, geometry/export acceptance
  and any normative ISO/IEC material needed for stronger claims.
- **Scope of execution policy:** whole-run versus branch gating, supported
  recovery after uncertain mutation and whether human approval is an initial
  requirement or the next profile.
- **Adoption and ownership:** independent implementer participants, test-harness
  home, maintainers, contribution/IP policy, document/code/test-data licenses,
  public distribution and conformance-mark policy. No terms or visibility
  changes have been selected.

The principal tradeoff is a deliberately smaller executable scope in exchange
for a credible, testable interoperability claim. Preserving the author's exact
tools and making missing prerequisites visible remain non-negotiable boundaries.
