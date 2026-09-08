# Decision 004: adoption path and unresolved gates

Status: recommendation for the experimental draft, 2026-09-07. Technical
implementation choices below are exercised in this repository; licensing,
publication, ownership and formal standardization decisions remain with the owner.

## Recommended decisions and tradeoffs

| Decision | Benefit | Cost or limit |
|---|---|---|
| Adopt CWL v1.2 for the fixed-call core | Existing graph semantics and two working execution engines | Batch/file staging is less natural for long-lived CAD sessions and human decisions |
| Adopt a small RO-Crate 1.2 profile | Familiar entrypoint, contextual metadata and transferable artifacts | Requires real minimum metadata and byte inventories; it does not resolve unavailable external resources |
| Reference MCP 2025-11-25 and pin captured tool contracts | Actual named tool communication, SDK/protocol conventions | MCP alone does not establish provider identity, resource equivalence or workflow semantics |
| Define exact intended binding, resource, diagnostic and acceptance rules here | Preserves the author's engineering choices and makes availability testable | Exact revisions reject unproven compatibility; provider-specific adapters remain necessary |
| Offer Python and independently implemented Node interfaces | New applications can consume installed artifacts without Wright | Shared upstream CWL parsing dependencies and repository authorship limit independence claims |
| Keep editing limited to preservation and explicit same-contract replacement | Small, reviewable revision with impact analysis and fresh acceptance | No automatic translation of CAD arguments, resources, geometry or AI-directed intent |
| Use local distribution artifacts and content identities first | Reproducible experimentation before release commitments | Technical reuse is not a grant of public redistribution or contribution rights |

The [working baseline](003-cwl-core.md), [core requirements](../spec/core-draft.md),
[conformance guide](../conformance/README.md) and
[adopter walkthrough](../tools/adopter-walkthrough/README.md) are the evidence
path. A finite passing suite supports its exact observations; it does not prove
all CWL, MCP, CAD or RO-Crate behavior. Reports correlate observed artifacts;
they are not cryptographic attestation against a malicious executor.

## What Wright would need

Wright currently has a richer native/canonical execution model and installation
bindings. Its source is not already a complete portable fixed-call definition.
Export requires all authoritative provider/application, operation/schema,
resource/revision, graph/input and acceptance facts. Local UUIDs and an accepted
canonical base cannot supply those facts to a recipient that does not have them.

The [versioned mapping](../docs/wright-compatibility.md) classifies direct facts,
explicit translation, preserved unsupported behavior and future Wright changes.
The external capture helper retains explicitly supplied original files and
reports gaps; it does not fabricate a conforming export. Converting an AI CAD
task into fixed tool calls creates an authored variant unless equivalence is
actually established. Wright import would preserve unavailable/unknown content
and provide explicit local binding and replacement actions.

## Prioritized next steps

1. **Freeze and review the experimental evidence.** Retain exact source,
   schema, fixture and distribution hashes with both full core reports and the
   isolated consumer walkthrough. Review failures and supported-role limits.
   Every semantic change after this freeze gets a new draft identity and tests.
2. **Capture one genuine Solid Edge fixture.** Obtain permitted native model
   bytes, freeze the actual provider build including relevant uncommitted code,
   capture real MCP negotiation/tool schemas/application identity and document
   resource-revision evidence. Follow the isolated-copy recipe. Exit: no invented
   pins, a complete authored fixed-call variant and independently checkable
   thickness/export criteria. Keep this gate unrun until prerequisites exist.
3. **Implement Wright export/import in a separately authorized Wright task.**
   Start with the captured fixed-call case. Test unavailable-provider import,
   no-op save, same-provider local/remote rebinding and explicit revision edits.
   Preserve original source and report every missing or translated fact.
4. **Prove real-provider interoperability on both engines.** Use independent
   working copies, retain original digests, verify exact document continuity and
   measured final results. Exercise partial export failure and uncertain
   mutation without replay. A mock pass does not satisfy these tests.
5. **Resolve distribution and participation terms before inviting adoption.**
   Review document/code/fixture licensing separately, contributor-IP policy,
   dependency obligations, project identity and maintainers. Then ask an outside
   implementer to build from the draft and public artifacts, retaining their
   interoperability report and documentation corrections.
6. **Expand only with demonstrated need.** Human approval needs authenticated
   decision authority, exact subject revisions, completeness, expiry/stale-result
   rules and independent negative tests. Stateful CAD/recovery, richer units and
   newer MCP protocol revisions each need a bounded profile and actual evidence.
7. **Consider stable governance after sustained interoperability.** Begin with
   a small documented maintainer review process and external test rounds. Assess
   a multi-vendor group or foundation when actual participants justify it; assess
   formal standardization when scope, IP, compatibility and stewardship are ready.
   A repository name or test badge does not establish recognition.

## Owner decisions still open

- **Licenses and IP:** a permissive code/test license with an appropriate
  specification license can lower implementation friction; a copyleft code
  option can require sharing modifications but adds integration obligations.
  Fixture/model permissions must be evaluated separately. DCO-style provenance,
  CLA-style grants and patent-policy approaches have different burden and rights
  consequences. The [research](../research/findings.md) records official sources;
  none of these terms is adopted here.
- **Stewardship:** owner-led review is inexpensive initially but concentrated;
  a multi-party group costs coordination and needs committed participants;
  foundation or formal-body processes add governance/IP overhead. Choose based
  on contributors and interoperability evidence, not anticipated prestige.
- **Provider trust:** which publisher-controlled identity and build/service
  evidence will establish real Solid Edge identity? Self-reported metadata and a
  matching tool schema are insufficient alone. The mock launcher pin proves only
  the explicitly stated fixture trust boundary.
- **Resource and compatibility policy:** exact native/cloud revision evidence,
  allowed provider updates, persistent result retention, capability expansion
  and migration/support windows need real integration evidence.
- **Public readiness:** visibility, publication, outside contribution,
  certification marks, stable compatibility and standards-body submission have
  not been authorized or achieved by this draft.

The project can be technically reusable now while these legal, product and
governance gates remain explicit. Passing the experimental core is the first
evidence milestone, not completion of the entire adoption path.
