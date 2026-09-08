# Concrete cases and interoperability experiments

Status: proposed test design, 2026-09-07. **None of these cross-installation or
independent-engine experiments has been run.** Only the existing Wright CAD
record identified below is observed evidence. Expected outcomes are proposed
requirements for review, not descriptions of working product behavior.

The [source-backed findings](../research/findings.md) explain the candidate
standards. The [Wright inspection](../research/wright.md) fixes the current
implementation baseline and its limits.

## Case 1: named Solid Edge MCP sheet-metal process

### Grounding and intended process

The inspected Wright fixture asks for a working copy of `cad-test/bracket.psm`,
changes `MaterialThickness` to 2.5 mm, hands the resulting application document
to another task, and exports STEP. Its recorded calls use `providerId: solid_edge`.
An existing recheck reports two 2.5 mm readbacks with 0.001 mm tolerance, native
and STEP artifact checks, and an unchanged original. It explicitly leaves human
acceptance pending. File paths, dates and SHA-256 identities are in
[the recorded evidence](../research/wright.md#engineering-examples-and-existing-evidence).

The fixture currently identifies a local MCP server UUID, and its tasks include
AI-driven behavior. It is not already a portable fixed-call process. Before
creating an executable exchange fixture, capture the intended server's publisher,
implementation revision, application provider/version, exact tool schemas and
native input bytes. Their absence is an unresolved fixture dependency; do not
invent identifiers or label a historical catalog pin as the running version.

**Proposed bounded process:** copy the identified original; open the copy with
the specified provider; perform the declared thickness change; rebuild and read
back the same document after mutation; save the native artifact; export the
declared STEP representation; record both outputs and acceptance evidence.
Tool names, schemas and order must come from the captured actual provider
contract. Author this fixed-call variant explicitly; do not claim it is a
lossless automatic translation of the existing AI tasks.

**Initial acceptance:** the final readback identifies the same provider and
document revision, thickness is within 0.001 mm of 2.5 mm, the original digest
is unchanged, and both outputs have recorded identities and sizes. These are
narrow checks. A later geometry/STEP profile must add declared export protocol
and geometric/PMI criteria before claiming AP242 or engineering equivalence.

### Transfer and failure outcomes

| Situation | Expected receiving-application behavior | Evidence needed |
|---|---|---|
| Same intended provider, different local server UUID/path | Map the logical requirement to the verified same implementation/application; map the input by identity; retain process bytes | Binding report identifies intended and observed provider/resource; no process edit from local rebinding |
| Linux recipient with no compatible local or remote provider configured | Display the named Solid Edge MCP block, its settings, inputs/outputs and connections; diagnose unavailable provider/execution target and gate affected work | Import/save preserves payload digests and graph facts; zero engineering calls. This is a scenario assumption, not a claim about vendor OS support |
| Same Linux authoring installation gains access to a supported remote Solid Edge service | Check remote provider, protocol, permissions and resource revision; execute there if the requirements match | Client OS alone does not reject an otherwise valid remote execution binding |
| Server is reachable but default provider has changed | Reject a provider mismatch for this process, even if tool names and schemas match | Test distinguishes application identity inside the server from connection identity |
| Correct service, missing native file or inaccessible cloud object | Preserve reference; distinguish absent, denied, wrong revision or unverifiable identity as available evidence permits | No substitution of a similarly named object; do not turn an ambiguous access error into a claim of deletion |
| User explicitly selects another CAD block | Create a new process revision, map settings/units and ports, reassess native/STEP representation compatibility and affected acceptance/approval | Reviewable edit identifies old/new provider, invalid mappings and affected downstream evidence; unaffected blocks preserved |
| Native save succeeds, STEP export fails | Retain verified native partial result and export error; mark required export incomplete and overall acceptance incomplete | Partial result has digest, provider/document provenance and durability; no fabricated STEP output |
| Connection drops after thickness mutation | Record an unknown operation outcome until the document can be identified and inspected | No automatic second mutation based only on transport retry advice; recovery checks exact working copy/revision |

Provider replacement can require rebuilding a native model and changing the
process's output contract. Importing STEP into another CAD application does not
prove equivalent sheet-metal features or authorize changing the original block.

### Candidate mapping

| Candidate | Concrete representation to evaluate | Decisive experiment |
|---|---|---|
| OWS 1.0.3 | Fixed MCP call tasks and explicit data handoff; package profile supplies intended provider/resource requirements | Two resolvers/executors enforce the provider inside the server, version pin, `isError`, document identity and partial-output rules |
| CWL 1.2.1 | CommandLineTool wrapper around the exact MCP adapter; required dependency and typed file/structured outputs | Can independent engines execute the wrapper and preserve diagnostics without hiding stateful document requirements? The adapter is part of the dependency contract |
| BPMN 2.0.2 | Service tasks, data associations and error paths with a declared MCP binding | Does a second engine execute that binding without vendor-specific reinterpretation? Model interchange alone does not pass |

The first candidate must pass the unavailable-provider case before any positive
CAD run. An engine that silently ignores the package's required binding profile
is ineligible, even if it accepts the workflow syntax.

## Case 2: calculation with explicit units and input provenance

**Proposed synthetic fixture.** Calculate the mass of a rectangular plate:
length 100 mm, width 80 mm, thickness 2.5 mm, density 7850 kg/m3. These are test
inputs, not a material specification or design recommendation. Declare the
quantity meanings and UCUM unit codes, input artifact digest, calculator
implementation/revision and result schema.

Expected volume is `0.1 × 0.08 × 0.0025 = 0.00002 m3`; expected mass is
`0.00002 × 7850 = 0.157 kg`. Use absolute mass tolerance `0.000001 kg` for this
fixture. Preserve the input identities and calculation expression in the
evidence; separately test equivalent input units, dimensional mismatch,
non-finite numbers and unavailable unit support. A unit label alone is not a
conversion implementation. [UCUM reference](https://ucum.org/ucum).

| Situation | Expected behavior |
|---|---|
| Same declared calculator/provider available | Execute against exact inputs; report 0.157 kg within tolerance with traceable expression and provider revision |
| Required calculator, package or compatible execution target unavailable | Preserve the calculation and requirements, diagnose availability, make no unannounced switch to another package or an AI mental calculation |
| Explicit replacement of calculator | Create a reviewed process revision; validate quantity meanings, units, rounding and output mapping using the same oracle |
| Calculation succeeds but result persistence fails | Distinguish a computed value from a durable output; retain trustworthy partial evidence and report persistence failure |
| Provider returns success with 157 kg, wrong dimensions, or missing provenance | Execution success remains distinguishable from acceptance failure or indeterminate evidence; no overall engineering pass |

**Candidate mapping.** CWL naturally expresses the typed file/parameter data
flow and a command-line calculator; OWS can call a declared calculator service
or command task. Use this simple case to isolate workflow and unit semantics
from CAD availability. Do not add DMN or a full SysML model merely to multiply
four quantities. Link those standards when richer constraints or engineering
models become actual requirements.

This is not claimed as a currently implemented Wright calculation workflow.
Wright's inspected analysis oracle provides a source-level precedent for
provider/resource provenance and exact unit checks, without general conversion.

## Case 3: inspection followed by human approval

**Proposed synthetic fixture.** Inspect an identified part revision against an
identified plan revision using a named inspection provider. For a small test,
two named holes each have diameter acceptance interval [5.95, 6.05] mm,
including endpoints. Results identify every required characteristic, method,
units and measured value; a real inspection profile also declares needed
calibration/uncertainty evidence. These values exercise the test, not a real
manufacturing release criterion.

The process checks completeness and each interval, then requires an authorized
human role to approve the exact definition, part, plan and result revisions.
Approval is not synthesized from an AI response, tool success or a passed
decision table. Changed evidence makes the corresponding prior approval stale.
QIF can carry quality artifacts; DMN can evaluate decision tables; BPMN can
express human process control. These remain distinct contracts.
[QIF](https://qifstandards.org/about-qif/),
[DMN 1.5](https://www.omg.org/spec/DMN/1.5),
[BPMN 2.0.2](https://www.omg.org/spec/BPMN/2.0.2).

| Situation | Expected behavior |
|---|---|
| Same provider and identified part/plan accessible | Execute inspection, validate completeness and measured criteria, then await the authorized human decision |
| Inspection provider, equipment resource, plan revision or required permission unavailable | Keep all inspection/approval blocks and references; diagnose the specific prerequisite; no fabricated measurement or automatic approval |
| User replaces inspection provider/block | Record a process revision; revalidate feature/datums/units mapping and measurement contract; invalidate affected acceptance/approval |
| First characteristic measured, second measurement fails | Retain the first measurement as partial; mark whole-plan acceptance incomplete; do not grant approval on partial success |
| All measurements pass, approver absent or declines | Execution and measured acceptance may pass, while approval remains pending or rejected |
| Result changes after approval | Preserve the historic approval attached to its original subjects; require a new decision for the changed result |

**Candidate mapping.** BPMN/DMN is the strongest comparison for this broader
human workflow. OWS needs a precisely defined external approval-service/event
contract, not a timer masquerading as approval. CWL can produce an inspection
report but is a weak first choice for a durable interactive approval process.
Wright's recovery model includes approval concepts, while its inspected native
compiler does not establish executable approval behavior. Keep this case as
an explicit next profile unless it is made a first-release requirement.

## Interoperability matrix and pass criteria

Tests below are proposed; all have status **not run**. Required diagnostic
categories refer to [the findings](../research/findings.md#6-validation-unavailable-resources-and-failure),
not invented wire codes. Each test records package/source digests, profile and
suite versions, exact implementation revisions, local binding evidence,
expected/actual observations and retained artifacts.

| ID | Test | Pass criterion |
|---|---|---|
| P01 | Import and no-op save, intended provider absent | Original authoritative/source artifact bytes and required block facts remain intact; absence diagnosed; no engineering calls |
| P02 | Unknown required profile/block plus optional metadata | Reader preserves both, identifies unsupported semantics, declines affected execution; optionality cannot erase a required binding |
| P03 | Known malformed graph or settings | Specific invalid-definition diagnostic; raw received data retained, distinct from missing dependency |
| P04 | Missing/corrupt packaged file, external reference retained | Digest mismatch or missing payload diagnosed; external requirement remains explicit; no filename-based replacement |
| B01 | Same provider, new endpoint/path/local UUID | Rebinding succeeds only with matching intended implementation/application and resource evidence; process identity unchanged |
| B02 | Same tool name on another server | Resolver refuses implicit substitution; intended server/provider remains visible |
| B03 | Same server, different default application provider | Resolver detects the mismatch before CAD mutation |
| B04 | Protocol/schema/application revision incompatibility | No call under an unproven contract; diagnostic identifies the version layer and expected/observed values |
| B05 | Correct remote provider from different client OS | Requirements evaluated against actual execution target and resource access; client platform alone does not remove the block |
| B06 | Permission denied, absent resource, wrong or unknown revision | Preserve reference and reported cause; decline execution where identity/access cannot be established |
| E01 | Positive deterministic calculation on two executors | Same traceable inputs and accepted quantity within specified tolerance; both outputs independently checked |
| E02 | Positive named-provider CAD handoff on two executors | Correct intended provider, same working-copy handoff, final readback, unchanged original and verified outputs |
| E03 | JSON-RPC failure, tool `isError`, malformed structured output | Distinct underlying causes retained; no false success from an HTTP/JSON-RPC response alone |
| E04 | Native output created then STEP export fails | Valid partial output retained and identified; required export and acceptance not falsely complete |
| E05 | Disconnect after possible mutation | Unknown outcome recorded; no blind replay; explicit resource inspection or user-directed recovery |
| A01 | Successful call with failing/missing acceptance evidence | Execution, acceptance and approval remain separate; absence is not treated as a passing measurement |
| A02 | Wrong units, equivalent units and non-finite quantity | Correct conversion when declared supported; otherwise explicit rejection/unsupported result, never guessed conversion |
| A03 | Partial inspection, denied approval, changed approved result | Completeness enforced and approval remains tied to exact subjects; historic evidence retained |
| R01 | Explicit provider replacement | New revision and reviewed mappings; only affected results/checks/approvals invalidated; unrelated content preserved |

### Independence and reproducibility

Use a small reader/resolver implemented from the proposed documents without
importing Wright's parser or canonical model. For execution, compare two
separately implemented workflow engines and binding adapters, and state any
shared dependencies. Sharing the intended CAD provider is necessary for this
case; sharing the workflow interpreter or provider resolver weakens the
independence claim for that layer. Two AI models driving one executor do not
count as two executors.

First use a deterministic fake MCP service that exposes intentionally conflicting
server/provider identities and controllable errors. It isolates negative paths
and runs without a CAD license. It cannot establish real CAD interoperability.
Then use the captured real Solid Edge contract and identical starting model
copies, under an explicitly prepared execution environment. CAD comparisons use
declared engineering tolerances and provenance; native files need not be
byte-identical across executions unless that is an explicit supported property.

Run P01–P04 and B01–B06 before real mutations. Run the calculation and fake-service
error cases next, then the real CAD case. A03 belongs to the approval-profile
stage. Publish individual results and failures instead of collapsing them into
a single “portable” score. Tests with unsupported scope are reported as such,
not counted as passing. Keep fixtures and assertions outside Wright's runtime
so an independent implementer can run them without Wright.

This document is the experimental design. Executable fixtures, validators,
license-cleared CAD samples and passing results are prioritized future work in
[the proposed decision](../decisions/001-first-boundary.md#prioritized-next-step-plan).
