# Goal brief: reusable process specification and implementer kit

Status: implementation brief activated on 2026-09-07; the experimental core and
implementer kit are now verified in the [goal audit](docs/goal-audit.md).
The text below remains the reusable objective for this milestone. Stable
standardization and public/legal release readiness are later gates; a new
`/goal` should identify the next bounded milestone rather than repeat completed work.

## Objective

Work in `D:/repos/engineering-process-spec`. Turn the existing research into a
small, reusable engineering-process specification and working implementer kit.
A developer or AI system using this repository and its declared upstream
standards must be able to create a supported process file and build a new
application that reads, preserves, validates, binds and executes it without
Wright, hidden Wright state, or undocumented knowledge from this conversation.

Deliver an experimental draft with actual schemas, semantic rules, examples,
adopter documentation, reusable tooling and passing conformance evidence.
Do not stop at another research report, architecture proposal or folder scaffold.

## Context and authorized scope

Read `AGENTS.md`, `VISION.md` and `RESEARCH.md` first, then the current research,
`decisions/001-first-boundary.md` and `use-cases/interoperability.md`. Preserve
their agreed author-choice and portability boundaries. Existing technical
recommendations are hypotheses to test, not automatically accepted standards.

This goal authorizes evolving this repository from research-only work into a
draft specification, schemas, examples, documentation, validation/conformance
tooling and small independent demonstration applications. Update repository
instructions and navigation to reflect that scope without erasing the research
or changing agreed invariants. Keep the structure small and organized around
what authors, application developers and maintainers need.

Wright remains read-only. Reconfirm its active checkout and inspect current
contracts, source, examples and existing evidence. Record exact commits and
identities of relevant uncommitted files; preserve all existing work. Do not
modify Wright or launch its applications/tests. Any compatibility/export
prototype belongs in this repository and must use documented, explicit inputs.

Do not change repository visibility, publish packages/releases, contact third
parties, select licensing or contributor-IP terms, or declare stable 1.0 or
standards-body recognition. Prepare concrete proposals for those later decisions.
Distinguish technical reusability from authorization for public redistribution.
Retain required upstream attribution/license notices for reused material;
preserving those notices does not select this project's licensing terms.

## Non-negotiable semantics

- Preserve the author's specific application, MCP implementation, application
  provider within that server, operation, version requirements, configuration,
  inputs, outputs and connections. A Solid Edge MCP block remains that block.
- Separate intended provider/resource identity from local endpoints, server
  UUIDs, paths, credentials and session handles. Rebinding a verified compatible
  instance of the same intended provider is local configuration. Replacement
  with another provider is an explicit process edit with a new revision and
  revalidation of affected mappings, connections, results and approvals.
- Missing applications, MCPs, platform support, permissions or resources do not
  erase blocks, corrupt definitions, remove requirements or trigger substitutes.
  An understood valid definition can be unavailable for execution. An unknown
  required feature is unsupported; a known violated rule is invalid. Preserve
  the received material and distinguish these cases.
- Applications own availability checks, diagnostics, execution gating and
  user-directed configuration/replacement. Specify the portable facts and
  observable behavior necessary to test those responsibilities, without
  prescribing a particular UI. Opening a process performs no engineering calls.
- Keep execution outcome, partial results, engineering acceptance and human
  approval distinct. A successful API call, AI narrative or file existing is
  insufficient engineering evidence. Specify behavior after a possibly applied
  mutation whose response was lost; do not imply rollback or safe replay.

## Deliverables

### 1. One implementable specification boundary

Choose one existing workflow representation through a bounded working
experiment. Start with the researched OWS/MCP candidate and compare the CWL
fallback where needed. Pin exact specification, protocol, schema, SDK and runtime
revisions; resolve documented incompatibilities. Use RO-Crate if its minimum
useful profile earns its implementation cost. Do not require multiple workflow
languages in the first profile, invent a new grammar, or hide a new task language
inside an ostensibly generic JSON wrapper.

Record the initial core after that experiment and before claiming conformance.
At minimum it includes fixed named MCP calls, explicit data handoff, a
deterministic calculation, preservation and provider/resource binding, failure
and partial outcomes, and acceptance evidence. Both independent execution paths
must pass this core, including MCP behavior; calculation alone is insufficient.

Write precise requirements with stable identifiers, normative versus
informative sections and explicit conformance roles: reader, editor, binder,
executor and provider adapter. Define the authoritative file/package entrypoint,
supported constructs and their execution meaning, data/quantity contracts,
provider/resource requirements, versioning, extensions, unknown-content
preservation, diagnostics and result/evidence records. Specify structural and
semantic validation separately. Each claimed mandatory behavior needs a
requirement-to-test mapping. Identify which rules come from upstream standards
and which this profile adds.

One authoritative process definition must contain or reference every required
semantic fact. Do not depend on Wright's accepted canonical base to recover
missing bindings, or maintain two independently editable authoritative graphs.
Supply machine-readable schemas and a semantic validator; schemas alone are
not the specification. Prefer a narrow, fully implemented core over declaring
broad unsupported semantics.

### 2. A complete path for a new application

Provide a small CLI/library and an integration example demonstrating this
sequence from a clean environment: load the file/package; identify its profile
and version; validate it; inspect its steps and requirements; preserve/save it;
resolve local bindings; preflight the intended resources; execute the supported
subset; inspect traceable outputs and acceptance results. A CLI is sufficient;
a new CAD GUI or general orchestration platform is outside this milestone.

Document the APIs or commands, extension/adapter boundary and error behavior.
A consuming project must be able to reference versioned schemas/fixtures and
use the tooling without copying this repository's internals into its application.
Provide reproducible local installation/use; public package publication remains
outside scope. Keep product integrations separate from the portable core.

Prove this path with a small application developed from the draft specification
and public examples, without importing Wright's parser, model or runtime. Use
a second independently implemented execution/binding path for the advertised
core subset. Prefer existing engines and separately implemented adapters;
two wrappers over the same interpreter/resolver do not prove independence at
those layers. Record shared dependencies and the exact scope tested. Two AI
models using one executor do not count, and repository-authored demonstrations
do not establish independent organizational adoption.

### 3. Honest Wright compatibility

Produce a versioned mapping of Wright's canonical contract, authoring source,
native compiler, provider bindings, artifact/resource handoff and run records
to the draft. Classify features as directly supported, explicitly translated,
preserved but unsupported, or requiring a future Wright change. Explain what
Wright would need to export and import the profile; implement only external
adapters that are feasible within the read-only boundary.

Show the exact input a new application receives, all additional required
artifacts and local configuration, and how it interprets the file without
Wright. Do not claim existing `.wflow` files already conform. Any conversion
must preserve the original source, expose missing authoritative facts and
document losses. Changing an AI-directed CAD task into fixed tool calls creates
an explicitly authored variant unless equivalence has actually been established.

### 4. Useful examples, with expected outcomes

Include a minimal complete process, the researched calculation with explicit
units and traceable inputs, and a clearly identified mock MCP process with
deterministic success and failure modes. These must run without Wright, paid
CAD software, credentials or model-provider API access. Give each example a
short explanation, declared dependencies, exact commands and expected results.

Include a named Solid Edge exchange case, particularly transfer to an
installation without the intended provider. Preserve its actual identity;
never present a mock as Solid Edge. Capture a runnable real-provider fixture
only from verified contracts and input artifacts available for that use.
Provide an opt-in integration recipe using isolated working copies. If the
provider, permissions, input rights or execution environment are unavailable,
mark real CAD execution unverified and state what is needed to run it.

Include explicit provider replacement and partial-result examples. Include the
inspection/human-approval case with clear scope: implement and test any claimed
approval behavior, or label it as a later profile/preservation-only example.
Do not imply an executable approval mechanism from a diagram or prose alone.
Add an authoring guide for both people and AI systems, including a validation
and correction loop that does not invent missing provider information.

### 5. Conformance, repository rules and adopter documentation

Turn the applicable proposed interoperability cases into executable tests with
machine-readable expected observations and reports. Cover no-op round trips,
unknown required features, malformed definitions, unavailable providers,
identical tool names on different servers, changed default application provider,
protocol/schema drift, incompatible or inaccessible resource revisions,
compatible remote execution, units, partial failure, unknown mutation outcomes
and explicit replacement. Verify process preservation as well as call results.

Run the tests for every claimed core role/profile on the independent paths.
Report passed, failed, unsupported and not-run results separately. A fake
provider proves protocol/binding behavior, not actual CAD behavior. Keep the
test harness usable outside Wright and document the consumer interface.

Provide a short README, repository map, quickstart, annotated example, “implement
this in your application” guide, conformance guide, diagnostic reference and
compatibility matrix. Verify the documented commands in a clean environment
with no Wright services, installed Wright package or hidden local state. Make
supported platforms and prerequisites explicit.

Add local/CI checks for schemas, semantics, examples, documentation links and
conformance reports. Define a lightweight change/proposal process, review rules,
draft versioning, compatibility/deprecation policy, extension ownership and
release-readiness checklist. Keep requirements, fixtures, tests and documentation
aligned through these rules. Prepare licensing/governance options and unresolved
decision records without adopting legal terms or claiming unrestricted reuse.

## Completion and working method

Work autonomously through reversible implementation choices. Delegate bounded
work and use a fresh implementer/reviewer to expose assumptions missing from
the documentation. Keep a concise progress/evidence record and revisit failed
design assumptions rather than weakening tests to obtain a pass. Use primary
sources and exact revisions for new technical decisions.

Complete this goal only when the draft's declared core has precise requirements,
working schemas/validation, runnable examples, passing required conformance
cases on two independent execution/binding paths, and a verified clean-environment
adopter walkthrough without Wright. Documentation and placeholder schemas alone
do not meet this condition. Failures in mandatory core work remain unfinished;
report a concrete blocker if no permitted path remains and continue unaffected
work while progress is possible.

Real Solid Edge execution, richer approval profiles, public distribution and
formal/stable standardization are separate readiness gates when their external
prerequisites are unavailable. Supply verified fixtures/recipes where feasible;
otherwise supply a capture plan, clearly non-executable template and precise
missing prerequisites without fabricating provider pins or model provenance.
Complete the mappings and gap reports, but do not count unrun integration tests as
passing or claim the broader gates are achieved. Do not drop requirements from
the declared core merely to declare the goal complete.

Finish with links to the implementation and documentation, exact commands run,
per-implementation conformance results, the Wright compatibility findings,
unresolved decisions and a prioritized path to real-provider interoperability,
external adoption and eventual stable standardization.

---

Goal framing follows the outcome, evidence and constraint approach in the
[official Codex Goals guide](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex).
The technical scope derives from this repository's research and proposed decision.
