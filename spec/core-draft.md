# Engineering process exchange core — 0.1.0-draft.1

Status: **experimental draft**. Requirements below define the target of
conformance tests. Support claims apply only to the exact source identities and
cases in a passing report. This document is the authority for the draft profile; research and
examples are informative. No stable standard or unrestricted redistribution
license is claimed.

The profile identifier is `urn:engineering-process-spec:core:0.1.0-draft.1`.
It profiles CWL v1.2 (specification/test text 1.2.1), RO-Crate 1.2 packaging and
MCP 2025-11-25. The initial project URNs identify this experimental contract;
they do not claim an external registry assignment or standards-body recognition.

## 1. Roles, authority and versions

**CORE-001 — Roles.** A reader inspects and preserves; an editor makes deliberate
definition changes; a binder resolves intended dependencies to receiving
configuration; an executor interprets the supported workflow; an MCP adapter
implements the binding/invocation contract. A conformance claim names its roles,
profile revision, test revision and implementation revision.

**CORE-002 — One process authority.** The package's CWL entrypoint supplies task
graph, expressions and data flow. Requirements refer to its nodes; they do not
define another graph. Original Wright source, when retained, is a source artifact
with an explicit mapping/loss report and is not a second editable authority.

**CORE-003 — Exact versions.** Profile, workflow language, process revision,
MCP protocol, implementation revision, application version, tool-contract snapshot
and resource revision are distinct. This core uses exact equality for declared
versions; no inferred compatibility ranges or silent upgrades are permitted.

## 2. Exchange package

**PKG-001 — Files.** A package is a directory or ZIP containing
`ro-crate-metadata.json`, `requirements.json`, the CWL entrypoint, its referenced
tool documents, input examples and tool-contract snapshots. ZIP members use
relative slash-separated paths. Absolute/parent paths, symlinks, duplicate
members and references escaping the package are invalid. JSON documents reject
duplicate object member names and non-finite numbers rather than selecting an
ambiguous value. Import may retain the
original archive for inspection; it must not materialize escaping members.

**PKG-002 — RO-Crate profile.** Metadata uses the RO-Crate 1.2 context. Its
metadata descriptor identifies `./` as the root Dataset. The root's `mainEntity`
identifies the CWL file, and `conformsTo` includes this profile. Every required
local payload is a File entity with its relative `@id` and SHA-256 of exact
bytes. `requirements.json` is included in `hasPart` and the file inventory.
The metadata file does not hash itself. The observed metadata-file digest and
all inventoried payload digests identify the package used by a run.
Retain RO-Crate's required root name, description, datePublished and license
properties. This core uses YYYY-MM-DD date precision. License may be nonempty
text or a reference to a described entity with name and description. The
repository's example statement records that licensing is undecided; it grants
no rights and selects no license. Its date is local draft availability, not
public release. The metadata descriptor is a CreativeWork. These minimums come
from [RO-Crate 1.2](https://www.researchobject.org/ro-crate/specification/1.2/root-data-entity.html);
inventory digests and the process entrypoint are this profile's additions.

**PKG-003 — Authoritative requirements.** `requirements.json` declares this
profile/version; a process ID/revision and CWL entrypoint; required features;
bindings; node-to-operation requirements; external resources; the default input
job; and acceptance criteria. The matching JSON Schema defines field shapes.
Unknown required features are unsupported, not silently ignored. Optional
metadata may be unfamiliar but must survive preservation.

**PKG-004 — Preservation.** Inspect, no-op save and transfer preserve original
payload bytes, metadata and unfamiliar content. Missing prerequisites cannot
delete/rewrite nodes or convert their operations. Invalid or unsupported input
is retained for diagnosis; interpretation/execution is declined where needed.
Opening/importing performs no engineering calls. Copying bytes is not an
execution-conformance claim.

## 3. CWL execution profile

**CWL-001 — Existing semantics.** Execute CWL Workflow/CommandLineTool graph and
data flow using the pinned engine. The profile permits standard parameter
references and the declared InlineJavascriptRequirement,
StepInputExpressionRequirement and MultipleInputFeatureRequirement. Required
unknown CWL features are unsupported. No host-specific callback supplies
undocumented graph meaning.
The exchange core uses packed JSON CWL, named input/output/step maps, one main
Workflow and fixed CommandLineTool adapters. Readers reject unqualified fields
that CWL does not define at document/process/step level. Preserve unfamiliar
namespace-qualified optional metadata. Subworkflows, conditional/scattered steps,
step-local execution requirements, base-URI overrides and adapter stream/exit-code overrides are
outside this core and are unsupported. The kit validates these core structural
and semantic constraints; the engine performs full upstream CWL validation before
executing. A core-reader result is not a general CWL conformance certificate.

**CWL-002 — Required extension.** The main workflow declares the required
`epx:ExchangeRequirement` using namespace
`epx: urn:engineering-process-spec:profile:` and references `requirements.json`.
A profile-aware driver validates and implements this requirement before
producing an ephemeral CWL execution copy with that consumed requirement
removed. It records the original and derived digests and this transformation.
It never overwrites the authoritative file. An engine that ignores the
requirement without implementing it does not conform to this profile.

**CWL-003 — Adapter invocation.** Fixed MCP nodes use a CommandLineTool whose
base command is `epx-mcp-call`. Its arguments identify the normalized workflow
node, logical binding, exact tool name, serialized JSON tool arguments and an
execution-context File. Node identities are `main/<step-key>` for this core's
`#main` workflow. The adapter validates the invocation against the node's
declared operation; mismatched binding/tool/node references fail before calling.
The process does not select a local Python/Node adapter implementation.
The core adapter's five inputs are context (File), node, binding, tool and
arguments_json (strings), with their matching CLI prefixes. Additional tool
command arguments, inputBinding valueFrom overrides and tool-level execution
requirements need a different declared profile; they cannot override the
verified invocation. Step-level CWL expressions construct arguments_json.

**CWL-004 — Local context.** The driver supplies the reserved CWL input
`epx_context` as a File. It describes validated package location, local binding
configuration, run ID and result/log locations. It is receiving-run configuration,
not a portable process requirement. Credentials remain in the receiving
environment. Neither context nor credentials are included in shared packages
or public reports. Existing CWL engines remain responsible for ordinary inputs,
argument expressions, staging and task scheduling.
Every step passes the reserved context input unchanged; it cannot replace it
with an author-supplied file or expression.

**CWL-005 — Handoff.** A successful adapter writes `result.json` containing the
original MCP CallToolResult and a separate call record. CWL file outputs and
expressions hand that result to subsequent nodes. The adapter does not perform
implicit downstream operations or infer data connections. All mandatory outputs
and node references must resolve; unsupported constructs do not become no-ops.
Core workflow outputs are explicit File outputSource references. Successful
execution also requires those engine outputs to exist and match their observed
call-result digests; successful node calls alone cannot prove workflow outputs.

## 4. Intended and observed provider identity

**BIND-001 — Intended provider.** Each logical binding requires implementation
identity and revision, application identity/version inside that implementation,
MCP protocol revision and allowed execution platforms. Tool descriptors are
separately pinned files. A local endpoint, server UUID, tool name, description or
matching schema alone cannot establish this identity.

**BIND-002 — Local evidence.** Receiving configuration identifies a stdio or
Streamable HTTP JSON-response connection and its trust basis. For a local
fixture, a verified launcher file digest and its explicit invocation establish
the limited test trust basis; they do not attest an entire dependency graph.
Remote configuration explicitly identifies the intended service/trust boundary.
No secret is inferred from or embedded in the process. Both the declared
identity evidence and observed MCP metadata must match before engineering calls.

**BIND-003 — Protocol observations.** Perform the MCP 2025-11-25 initialization
and initialized notification; verify the negotiated protocol and capabilities.
The core adapter metadata key is the valid experimental MCP `_meta` key
`engineering-process-provider`, containing implementation, revision, application,
applicationVersion and executionPlatform. Values are compared with requirements.
The mock fixture supplies this metadata; a real provider lacking this profile
needs an explicit verified adapter, not fabricated self-reported values.

**BIND-004 — Tools.** Resolve the exact server-scoped tool name only on the
intended binding. Compare discovered name, inputSchema and outputSchema with
the pinned descriptor as JSON values; its file digest pins the captured bytes.
Object-member ordering is immaterial for this comparison; JSON types matter.
This is not a new semantic-hash standard. Validate arguments and successful
structured output with JSON Schema Draft 2020-12.

**BIND-005 — Availability.** A missing provider, incompatible version/platform,
changed default application, inaccessible resource or unverifiable identity
gates affected execution and preserves the package. This core conservatively
gates the whole run at preflight. Recheck binding/resource requirements at
invocation to detect changes after preflight. Evaluate platform support against
the execution target rather than the author's client OS.

**BIND-006 — Replacement.** Configuring a different verified connection to the
same intended provider does not change process revision. A different provider
requires an explicit edited package with a new process revision, updated node
contracts and validated connections. Preserve unaffected artifacts; re-evaluate
affected acceptance/results and any existing approval subjects. Equal tool
names/schemas cannot authorize replacement.

## 5. Resources and tool effects

**RES-001 — Resource identity.** A packaged file is identified by inventory
digest. An external resource declares binding, URI and exact revision.
Resource access must establish the intended provider/object/revision before
dependent calls. The core mock resource representation is JSON text containing
`id`, `provider` and `revision`; provider-specific real adapters must document
their equivalent evidence rather than assume a generic URI proves identity.

**RES-002 — Access failure.** Distinguish absence, denial, wrong revision and
unverifiable state using available evidence. Do not infer deletion from an
ambiguous authorization response. Preserve the original requirement. No
similarly named object or neutral-format file is an implicit substitute.

**RES-003 — Effects and uncertain outcomes.** Each declared operation identifies
read-only or mutation effect. A lost response after a possible mutation yields
unknown outcome, without implied rollback or automatic replay. A disconnect
before engineering invocation is unavailable; a known tool/protocol failure is
execution-failed. Resume/retry requires an explicit later policy; this core
performs no automatic engineering-call retry.

## 6. Results and engineering acceptance

**OUT-001 — Recorded execution.** Run reports identify profile/implementation
versions; conformance reports additionally identify the test revision. Record
package/process/input digests, run/node IDs, intended and observed
provider/resource revisions, request/result evidence, output digests and
durability. Retain native error causes. Reports exclude credentials and local
secret configuration. Succeeded/failed/unknown/blocked execution states are
separate from acceptance and approval state.

**OUT-002 — Partial results.** Preserve successful upstream call records and
output artifacts when a later node fails. Their identities, provenance and
durability remain explicit. Do not invent a failed node's output or label a
required missing output complete. Unknown mutation has priority over an
ordinary failure when the available evidence cannot establish its outcome.

**OUT-003 — Failure channels.** JSON-RPC errors, CallToolResult `isError`, invalid
structured output and lost responses are distinct retained causes. HTTP success
or an engine exit code alone does not prove successful engineering execution.

**ACC-001 — Quantity criteria.** Each criterion identifies a node/result JSON
Pointer, quantity meaning, value/unit pointers and expected value with absolute
tolerance or inclusive bounds. Values and bounds must be finite. Validate the
quantity and dimensions before comparing. The initial unit table supports
length m/mm, mass kg/g, volume m3/mm3 and density kg/m3/g/cm3 using explicit
conversion factors; other units are unsupported, never guessed.
Validate the declared criterion's unit/dimension at definition time; an unknown
conversion is unsupported and an incompatible dimension is invalid. At execution,
validate the observed quantity separately before applying the criterion.

**ACC-002 — Evidence and status.** Acceptance evaluates the actual observed
successful tool result tied to the run, node, provider and output digest. A
matching synthetic value or unrelated file is insufficient. Report pass, fail,
indeterminate or not-run per criterion and overall. Failure of required
acceptance prevents an overall accepted result even when execution succeeded.
Aggregate criteria as follows: any fail yields fail; otherwise any indeterminate
or a mixture of pass and not-run yields indeterminate; all not-run yields
not-run; all pass yields pass. Partial measurement evidence is not a complete
acceptance verdict. Digest correlation records observed evidence integrity;
this core does not provide signed attestation against a malicious executor.

**ACC-003 — Approval.** Human approval is a separate subject-bound decision.
This core does not implement human authorization or a durable approval service.
Preserve referenced evidence and identify unsupported required approval features.
Never infer human approval from an AI verdict, timer, measurement or tool call.

## 7. Diagnostics and conformance

**DIAG-001 — Categories.** Diagnostics have a stable code/category, requirement
ID and explanatory message. Include the affected node/dependency or document
pointer when known, expected/observed evidence for mismatches, and native cause
when available. Do not invent values that could not be observed. Distinguish invalid, unsupported, unavailable,
execution-failed and outcome-unknown. Presentation and recovery UI belong to
the receiving application.

**CONF-001 — Evidence scope.** Map every mandatory requirement to a fixture/test
and actual implementation result. Report pass/fail/unsupported/not-run rather
than treating skips as success. The two core execution/binding paths must pass
the same fixed-MCP, handoff, preservation, failure and acceptance cases.
Mocks establish their stated protocol/binding behavior only; real Solid Edge,
organizational adoption and stable release are separate gates.

## Upstream authority and implementation status

The [source register](../research/sources.md) identifies the authoritative CWL,
MCP, JSON Schema, UCUM and RO-Crate versions. The experimental engine choice is
documented in [Decision 003](../decisions/003-cwl-core.md). Use the
[conformance guide](../conformance/README.md) and
[goal audit](../docs/goal-audit.md) to assess the precise demonstrated scope.
