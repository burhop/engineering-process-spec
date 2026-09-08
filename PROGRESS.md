# Implementation progress and evidence

Goal activated 2026-09-07 under [IMPLEMENTATION_GOAL.md](IMPLEMENTATION_GOAL.md).
The experimental kit is implemented and verified for its declared core. No stable release, public-distribution
readiness or real-CAD interoperability is claimed.

## Implemented boundary

[Decision 003](decisions/003-cwl-core.md) selects CWL v1.2 after actual OWS and
CWL experiments. Synapse's tested revision rejected the MCP function despite
exit code zero; both selected CWL engines executed file handoff. The
[baseline evidence](experiments/workflow-baseline/README.md) records exact source,
engine, image and dependency identities.

The [core draft](spec/core-draft.md) defines 29 requirement IDs and uses RO-Crate
1.2, MCP 2025-11-25, JSON Schema and a bounded explicit unit table. It preserves
exact provider/application/tool/resource choices, separates local configuration,
and distinguishes invalid, unsupported, unavailable, failed and unknown outcomes.

The locally installable Python/cwltool and independent Node/StreamFlow paths
implement readers, binders, adapters, execution and acceptance. Editing is
limited to preservation and explicit same-contract provider replacement with a
new revision, retained original requirements and affected-acceptance review.
The [compatibility matrix](docs/compatibility.md) describes shared dependencies
and the exact scope; no outside organizational adoption is claimed.

## Verification record

- Generated example payloads and inventories verify deterministically: minimal,
  volume-to-mass calculation, three-call mock mutation, explicit replacement and
  preserved unsupported human approval. No mock is presented as Solid Edge.
- The first complete frozen candidate passed 112 core observations with eight
  later-gate observations not run. Review then exposed numeric conversion
  overflow, which was corrected rather than omitted from the final suite.
- The final suite passed **60/60 mandatory cases on each implementation**, mapping all 29 requirements. The [retained report](conformance/results/2026-09-07/report.json) records **120 passed, zero failed, zero unsupported and eight later-gate observations not run**. Its [raw evidence archive](conformance/results/2026-09-07/evidence.zip) retains all 3,493 original per-case files with checked digests.
- The [maintained consumer walkthrough](tools/adopter-walkthrough/README.md)
  installs only copied distribution artifacts, the public example and explicit
  mock provider. Its container has no repository/Wright mount or network. The
  [evidence receipt](docs/adopter-evidence.json) identifies the actual version
  tested; historical local outputs remain separate.
- Focused current tests: six Python input/acceptance/preservation tests, five external
  Wright-capture tests, 15 Node tests and 25 mock MCP protocol tests pass.
  Linux repository checks validate three schemas, five example packages, fixture
  drift, local documentation targets and requirement mapping.
- The [review findings](docs/review-findings.md) record concrete defects and
  fixes, including CLI exit status, CWL/profile metadata validation, strict input
  values, acceptance aggregation and finite conversion. Dependency advisories
  were checked against their actual paths and patched/removed; npm audit's zero
  findings is a dated database observation, not a security certification.

The [goal audit](docs/goal-audit.md) tracks each promised deliverable. The
[conformance guide](conformance/README.md) explains negative-case passes,
unsupported/not-run states, original CAD cases versus mock adaptations, and
how to reproduce the same black-box interface.

## Commands and reproducibility

From the installed kit and declared runtime environment:

```sh
python tools/check.py
npm test --prefix applications/node
python tests/providers/test_mock_mcp.py --report NEW_REPORT.json
python tests/conformance/run_core.py --jobs 4 --out NEW_EVIDENCE_DIRECTORY
python tools/check.py --report NEW_EVIDENCE_DIRECTORY/report.json
```

Use the [walkthrough command](tools/adopter-walkthrough/README.md) with explicit
local wheel/tarball arguments to verify a new consuming application. The
[quickstart](docs/quickstart.md) documents ordinary isolated builds; that build
path and copied-artifact installs were exercised. Exact distribution hashes
identify tested artifacts; byte-reproducible builds are not claimed.

The [CI recipe](tools/ci.sh) uses these same checks and the isolated consumer
harness. Its shell syntax and command paths were checked locally; no hosted
GitHub Actions run is claimed. Local CI output directories must be fresh.
External links and Markdown anchor spelling are outside the local-link checker.

## Wright and later gates

The [Wright inspection](research/wright.md) reconfirms the active nested
checkout, commit, relevant dirty-file hashes and source-versus-recorded-behavior
limits. Wright was not modified or launched/tested. The external
[capture helper](tools/wright_capture.py) preserves explicit originals and
reports missing facts; it does not produce a conforming `.wflow` conversion.

Real Solid Edge requires an authentic pinned provider build, captured contracts,
permitted native model bytes and a prepared isolated environment. Rich human
approval requires a separate implemented profile. Licensing/IP, publication,
outside adoption and stable/formal standardization remain unresolved gates.
[Decision 004](decisions/004-adoption-readiness.md) recommends the next steps and
states their tradeoffs.
