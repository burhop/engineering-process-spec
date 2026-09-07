# Research brief

Read VISION.md first. Research must help us choose a practical approach compatible
with Wright and attractive to independent creators and executors. Produce
evidence-backed decisions, not an encyclopedic catalog or an invented grammar.

## Questions to answer

1. Existing standards: Which parts already cover process structure, decisions,
   engineering semantics, model/resource identity, manufacturing operations,
   units, verification, and execution results? What should we adopt, reference,
   extend, or define? Keep process definitions distinct from communication protocols.
2. Implementations: What independent parsers, editors, executors, validators,
   SDKs, and conformance suites actually exist? Can another implementer use the
   specification without the original author's runtime? What interoperability
   limitations, round-trip losses, or vendor-specific extensions are documented?
3. Sharing and communication: How are definitions distributed, discovered,
   versioned, packaged with dependencies, exchanged as files or messages, and
   bound to installation-specific connections? How are specific MCP/provider
   identities retained without embedding credentials or changing tool choices?
4. Portability and failures: How are valid-but-unexecutable processes represented?
   What happens with missing tools, unsupported versions/platforms, inaccessible
   resources, unknown extensions, partial execution, or user-directed replacement?
   Separate language requirements from application responsibilities.
5. Adoption: What makes a specification easy and worthwhile to implement? Study
   quickstarts, examples, implementation size, validators, diagnostics, test kits,
   compatibility badges, extension registries, contribution processes, governance,
   and specification/code licensing and IP policies. Present licensing options;
   do not adopt terms or claim legal clearance on the owner's behalf.
6. Standardization: Compare a project-led open specification, multi-vendor working
   group, foundation/consortium stewardship, and formal standards-body submission.
   Identify evidence and participation needed at each stage; avoid speculative
   adoption promises or assuming formal recognition must come first.

## Initial research map

Use primary specifications and official implementation repositories. Verify
current versions, dates, maturity, and repository status; an old publication date
alone does not make a standard irrelevant. Include MCP explicitly. The following
are research leads, not selected dependencies or assertions of suitability:

- Process/decisions/execution: BPMN, DMN, Common Workflow Language.
- Engineering/design: SysML v2/KerML and its APIs, STEP/AP242; investigate
  STEP-NC/AP238 if manufacturing-process semantics are relevant.
- Manufacturing exchange: ISA-95/B2MML, AutomationML; consider OPC UA where it
  addresses resource/service communication rather than process meaning.
- Verification/quality: QIF; investigate provenance standards where useful.
- AI/tool communication: MCP specification, schemas, SDKs, registry, governance,
  and error/capability conventions; A2A as an adjacent communication model.
- Dependency precedent: Python packaging/version/platform metadata, including
  what it solves and what remains an application/runtime concern.
- Implementation collaboration: CAx/MBx interoperability test rounds and
  recommended practices; comparable open-specification proposal/conformance models.

Starting points (follow official links to specifications and repositories):
- https://modelcontextprotocol.io/specification/
- https://github.com/modelcontextprotocol/modelcontextprotocol
- https://a2a-protocol.org/latest/specification/
- https://www.commonwl.org/specification/
- https://www.omg.org/spec/BPMN/
- https://www.omg.org/spec/DMN/
- https://www.omg.org/spec/SysML/
- https://www.mbx-if.org/home/cax/implementor-group/
- https://www.automationml.org/about-automationml/specifications/
- https://mesa.org/topics-resources/b2mml/
- https://qifstandards.org/about-qif/
- https://packaging.python.org/en/latest/specifications/
- https://www.iso.org/stages-and-resources-for-standards-development.html

## Ground the comparison in cases

Use three small cases: (1) a named Solid Edge MCP sheet-metal operation with
measured acceptance criteria, (2) an engineering calculation with explicit units
and traceable inputs, and (3) a manufacturing/inspection process requiring human
approval. These are proposed cases until verified against working Wright behavior.

For each, examine same-provider execution, unavailable provider/platform, explicit
block replacement, and partial failure. Distinguish same-provider portability
from a proposed conversion to a different tool. Two AI models using the same
executor do not establish independent executor conformance.

## Wright inspection

Inspect D:/repos/wright read-only. The active implementation checkout confirmed
on 2026-09-07 was D:/repos/wright/.local-run/epp-f02b-writer/wright; confirm it is
still active before treating it as current. Start with the contracts under
specs/080-canonical-workflow-recovery/contracts and relevant parsers, schemas,
examples, and tests. Cite exact commits and paths; label uncommitted observations
with their observation date and content identity. Do not claim behavior from
planning documents alone. Do not change Wright or run its applications/tests
merely to perform the initial research; identify focused experiments separately.

## Deliverables and sequence

1. Inventory current Wright semantics, portability gaps, and unknowns.
2. Create a compact comparison matrix and source register: official version,
   publication/retrieval dates, links, implementations, evidence, and limitations.
3. Work the concrete use cases through the most relevant candidates. Go deep on
   the strongest fits, rather than giving every candidate equal research effort.
4. Recommend adopt/reference/extend/define choices, alternative approaches, and
   a small initial interchange boundary. Separate documented facts, demonstrated
   implementation behavior, hypotheses, and proposed requirements.
5. Organize this repo minimally into research/, use-cases/, and decisions/ based
   on those findings. Decision documents remain proposals until accepted. Provide
   a prioritized plan for examples, conformance tests, independent implementation,
   developer onboarding, and eventual governance.

Summarize findings for the owner with a comparison table and a simple boundary
or handoff diagram where useful. Link detailed evidence. Explicitly identify
paywalled/inaccessible normative material and do not infer its contents. Do not
copy copyrighted standards into the repository. Do not publish a stable version,
change repository visibility, contact third parties, or choose licensing terms.
