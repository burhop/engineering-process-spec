# Research agenda

Read [VISION.md](VISION.md) first. The [19 October code review](research/wright-code-review.md)
now inventories Wright's implemented transfer, instruction, interaction, validation
and UI boundaries, including local unpublished work. The [interchange draft](spec/interchange-draft.md)
turns those findings into proposed requirements without selecting a new grammar.

## Immediate questions

| Priority | Question | Required evidence / next deliverable |
|---|---|---|
| 1 | What provider identity survives a move between installations? | Work a real same-provider binding through two workspaces; separate provider/application/version/resource identity from local connection IDs and secrets |
| 1 | What exact source subset can another executor implement? | Freeze supported step/port/control semantics with positive and negative vectors; distinguish parse/import from executable validity |
| 1 | How are dependencies and unknown extensions preserved? | Inventory declared versus implicit files/resources; define opaque preservation and mandatory-extension rejection without data loss |
| 1 | Can two implementations reproduce package identities? | Cross-language UTF-8, newline, Unicode, numeric and canonicalization vectors; do not assume a JSON label defines identical hashing |
| 2 | What model portability is intended? | Preserve instructions and typed policy; decide treatment of workspace defaults, permitted substitutions and observable routing identity |
| 2 | Which evidence can be shared without transferring authority? | Define optional result/reference exchange separately from live run migration, answers, approvals and credentials |
| 2 | How much presentation belongs in interchange? | Versioned bindings and common fallback; separate portable interaction meaning from Wright client/kit code and local build trust |
| 3 | Which existing standards should be adopted or profiled? | Compare the concrete cases and implementation effort against official specifications and independent tools |

## Standards comparison remains open

The following are research leads, **not selected dependencies or claims of current
version, suitability or implemented mapping**. Verify official versions, maturity,
implementations and limitations when conducting that comparison.

| Area | Starting points | Compare against our needs |
|---|---|---|
| Process/decisions | [BPMN](https://www.omg.org/spec/BPMN/), [DMN](https://www.omg.org/spec/DMN/), [CWL](https://www.commonwl.org/specification/) | Typed handoffs, supported graph semantics, human decisions, bounded recovery and implementation size |
| Engineering models | [SysML](https://www.omg.org/spec/SysML/), [CAx implementor group](https://www.mbx-if.org/home/cax/implementor-group/) | Requirements, engineering/resource identity and interoperability practices; investigate STEP/AP242 and STEP-NC/AP238 where applicable |
| Manufacturing exchange | [AutomationML](https://www.automationml.org/about-automationml/specifications/), [B2MML](https://mesa.org/topics-resources/b2mml/) | Process/resource meaning versus application-specific execution; investigate ISA-95 and OPC UA at the relevant boundary |
| Verification | [QIF](https://qifstandards.org/about-qif/) | Measurements, tolerances, verification/provenance and exact subject identity |
| Tools and agents | [MCP](https://modelcontextprotocol.io/specification/), [MCP source](https://github.com/modelcontextprotocol/modelcontextprotocol), [A2A](https://a2a-protocol.org/latest/specification/) | Capability/resource communication versus reusable process definition semantics |
| Dependencies | [Python packaging specifications](https://packaging.python.org/en/latest/specifications/) | Version/platform requirements, dependency identity and the boundary to local environment readiness |
| Standardization | [ISO development stages](https://www.iso.org/stages-and-resources-for-standards-development.html) | Evidence/participation needed after a useful independent implementation exists |

The October update reviews Wright code; it does not claim to have completed this
standards survey or read paywalled normative material. Do not copy standards text
or infer inaccessible requirements. Use primary sources and exact revisions.

## Practical sequence

1. Resolve provider/resource binding and the first executable subset using the
   [existing engineering cases](use-cases/README.md).
2. Publish representative packages, digest vectors and expected diagnostics.
3. Build an independent reader, then a bounded executor; publish the
   [per-role conformance evidence](conformance/README.md).
4. Compare the strongest standards candidates against the same cases. Recommend
   adopt/reference/extend/define choices and costs, not an encyclopedic catalog.
5. Propose versioning, extension, governance, licensing and contribution terms for
   explicit owner decision. Stable 1.0 or standards submission follows evidence.

## Repeatable Wright inspection

Do not assume a historical Windows path or the current working directory is the
latest implementation. Discover the active checkout and registered worktrees,
record remote branch heads, compare local commits and inspect relevant dirty files
read-only. Use exact public commit links for published code and content hashes for
local-only material. Keep implementation, proposed work, retained test evidence,
newly verified behavior and user acceptance distinct.

Start with the current owners in `packages/core/src/core/` and
`packages/workspace_service/src/workspace_service/`, their tests, and the canonical
editor/source contracts. Features 080, 082 and 083 provide architectural context;
old plans can contain historical findings superseded by code. Keep model adapters,
frontend hosting and the shared executor separate in any portability claim.

Do not change Wright, install providers, start runs or consume review authority
merely to update this review. Focused future interoperability experiments require
an explicit scope and fresh isolated subjects. Preserve existing local work.
