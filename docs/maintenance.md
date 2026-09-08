# Maintaining the experimental draft

Status: working draft, 2026-09-07. These rules keep the specification, adopter
kit and evidence consistent during implementation. They do not establish a
stable compatibility promise, certification program or external contribution
terms. Follow [CONTRIBUTING](../CONTRIBUTING.md) for individual changes and the
[goal audit](goal-audit.md) for completion evidence.

## Change and version rules

Record the selected workflow baseline and supported core in a decision before
claiming conformance. A semantic change identifies the affected requirements,
motivating example, alternatives, compatibility consequences and test changes.
The review should answer whether an independent application would interpret an
existing process differently. If so, it is not an editorial correction.

| Change | Required handling |
|---|---|
| Editorial clarification with unchanged accepted inputs/behavior | Record the repository revision and check references/examples; keep semantic identity only if behavior is unchanged |
| Changed required field, validation rule, execution meaning or required upstream contract | Assign a new draft profile revision; update fixtures and supported-version matrix; preserve prior evidence |
| Added optional extension | Give it an owned namespace and explicit version; test preservation and whether ignoring it is permitted |
| Removed or deprecated feature | Describe replacement/migration, affected versions and execution impact; retain readable original material and tests for unsupported handling |
| Changed provider or operation in a process | Create an explicit process revision and revalidate affected bindings, data and evidence; never treat it as local configuration |

The first passing experimental report freezes its exact source/content identity.
Earlier development and failing probes are explicitly working candidates, with
their own hashes; they are not a released immutable draft. After that freeze,
never attach different normative content to an already recorded draft identifier.
Before stable compatibility rules exist,
claim compatibility only for the exact profile revisions tested. A newer schema
or SDK does not automatically establish compatibility. Do not claim general
version-range support from exact-version tests.

Keep profile, process, workflow-language, MCP, schema, implementation, provider
and test-suite versions distinct. Published upstream identifiers retain their
own version schemes. Repository commit/content identities locate the exact
artifacts and reports behind a claim. Decide any stable version-numbering and
support-window promises through the later readiness process.

Deprecation notices state what changes, why, the affected versions, migration
instructions and the last tested behavior. A migration creates reviewable new
process material and preserves its source. It must not remove a missing provider
or convert an AI-directed task into fixed calls while claiming equivalence.
No draft deprecation implies an unstated support duration.

## Keep the contract and kit aligned

Each mandatory requirement has a stable ID, an applicable role/profile and
observable pass criteria. Maintain a trace from that ID to structural schema
constraints where applicable, semantic validation, positive/negative fixtures,
test IDs and per-implementation reports. Rules a schema cannot express still
need prose and executable evidence. Do not recycle requirement IDs for different
meanings or edit expected results merely to match an implementation bug.

Examples name their authority, required files, dependencies, commands and
expected outcomes. Invalid, unavailable and unsupported examples say which
outcome is intentional. A non-executable CAD template is never presented as a
runnable fixture. Reused material keeps its source revision and required notices;
new evidence follows the [source-register conventions](../research/sources.md).

Keep old reports associated with their original input, profile, suite and
implementation identities. New results supersede claims only for the scope they
actually test. Test changes that narrow an assertion require an explicit reason
and review against the original requirement.

## Extensions and identity

An extension declares a namespace its publisher controls, version, specification
reference, required/optional status and affected semantics. Do not claim another
organization's namespace or infer publisher authority from a friendly name.
Local experimental identifiers must be labelled local and must not pretend to
be official vendor identifiers. A general extension registry is unnecessary
until actual independent extensions justify it.

Unknown required semantics prevent the affected execution claim while preserving
the received content. Optional metadata may be ignored only when doing so cannot
change process meaning. Provider identity, resource requirements and acceptance
rules cannot become optional metadata to bypass enforcement. An editor that
cannot preserve an unfamiliar construct must decline the unsafe edit rather
than silently discard it. Namespace ownership does not prove that an installed
provider or service has the intended implementation identity.

## Checks and evidence

Install the local kit and declared runtimes using the [quickstart](quickstart.md).
Local and CI checks use the same underlying commands below. Use a new evidence
directory for every conformance/walkthrough run and retain failed observations.
The [Linux CI recipe](../tools/ci.sh) and
[workflow definition](../.github/workflows/check.yml) run the checks; creating
those files does not claim that a hosted CI run occurred.

| Check interface | Required outcome | Command/status |
|---|---|---|
| Schema and semantic validation | Valid fixtures accepted; intended invalid/unsupported cases diagnosed correctly | `python tools/check.py`; `python tools/build_examples.py --check` |
| Core conformance by implementation | Required reader/editor/binder/executor/adapter behavior tested through both engines | `python tests/conformance/run_core.py --out NEW_DIRECTORY` |
| Runnable examples | Minimal, calculation and mock MCP produce actual declared observations | Core suite plus [example commands](../examples/README.md) |
| Documentation | Local link targets and generated fixtures checked; commands exercised by the maintained consumer harness | `python tools/check.py`; [walkthrough](../tools/adopter-walkthrough/README.md). External link availability and Markdown anchor spelling are not checked by this script. |
| Report/coverage consistency | All required cases/requirements pass and tested source hashes match | `python tools/check.py --report REPORT_DIRECTORY/report.json` |
| Clean adopter walkthrough | Install and use only public artifacts in an isolated consumer | [Exact maintained command](../tools/adopter-walkthrough/README.md); no Wright or source-tree mount |

Also run `npm test --prefix applications/node` for schema drift and focused
Node invariants, and `python tests/providers/test_mock_mcp.py --report NEW_FILE`
for the mock's protocol tests. The retained [audit](goal-audit.md) links actual
results. Passing the repository check without `--report` is not full conformance.

CI definitions alone do not prove a hosted CI run occurred. Record whether
evidence came from local execution or CI, the platform/prerequisites and exact
commands. Run focused checks appropriate to the change; broaden testing when
changed behavior, failures or unresolved concerns justify it. A blocked real
provider integration does not prevent running unaffected core checks.

## Conformance claims

A conformance report identifies the implementation and source revision, claimed
role/profile, upstream and tool/provider versions, suite revision, fixture/input
digests, local binding evidence, platform, timestamp, exact commands and retained
outputs. Every case records expected/observed behavior and one of `passed`,
`failed`, `unsupported` or `not run`, with a reason when it did not pass.
Reports must not include credential values.

Summaries include denominators and every required case; filtering failures or
excluding unsupported mandatory cases invalidates a claim for that profile.
Schema validity, a successful tool call or a mock-only run does not establish
engineering acceptance or real CAD interoperability. Distinguish independently
implemented interpreters and binding adapters from shared dependencies. Two
wrappers around one interpreter, or two AI models using one executor, do not
establish independent conformance at those layers.

Use narrowly qualified statements such as "implementation revision X passed
the listed reader tests for draft Y on platform Z; executor cases were not run."
Fill in actual identities and link the report. Do not introduce a certification
badge or claim compatibility with untested profile/provider versions. Follow
the [interoperability test design](../use-cases/interoperability.md) and preserve
the distinction between mock adaptations and original real-CAD cases.

## Readiness gates

| Gate | Evidence or owner decision required before claiming it |
|---|---|
| Experimental core complete | [Goal-audit core criteria](goal-audit.md) demonstrated, two independent execution/binding paths passing the required core, and verified clean adopter walkthrough |
| Real CAD interoperable | Authentic provider/contracts and permitted input artifacts, isolated-copy recipe and actual independent same-provider runs, unavailable-provider behavior and controlled failures |
| Rich approval profile | Implemented approval authority, exact subject revisions, completeness and stale/denied/partial-result tests; diagrams are insufficient |
| Public distribution/contribution ready | Owner decisions on document/code/test-data licensing, contributor-IP and governance; upstream notice obligations and fixture rights recorded; publication/visibility authorization obtained separately |
| Stable or formally standardized | Sustained independent implementation evidence, reviewed compatibility/migration commitments, ownership/governance and separately authorized release or standards-body process |

Prepare concrete options and missing-prerequisite records for unresolved gates.
Do not add project license terms, a CLA/DCO requirement, patent commitments or
trademark/certification terms by implication. Retaining upstream notices fulfills
existing material requirements; it does not choose this project's terms. No
public release, third-party contact or visibility change is authorized by these
maintenance instructions.
