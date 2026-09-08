# Experimental core demonstration

The [retained report](report.json) records **120 passed, 0 failed, 8 not run**:
all 60 mandatory core cases passed on each application, with all 29 draft
requirements covered by their mapped assertions. The four later cases are
reported separately for both applications. The run completed on 2026-09-08 UTC
(2026-09-07 in the project owner's local timezone).

| Application | Actual workflow engine | Distribution SHA-256 |
|---|---|---|
| Python kit 0.1.0.dev1 | cwltool 3.2.20260720092025 | `2965362c13a5132d19d8dbc6fd67066a0fb97d65c5f2d913886b26e5394509a3` |
| Node adopter 0.1.0-draft.1 | StreamFlow 0.2.0rc2 | `84f5d664992274ae7d6c65433f7f386f96ea4aa4c8209d2461d6d96d07258843` |

Both paths ran in a disposable Linux container with Python 3.12.14 and Node
24.13.1, without Wright. Python was installed from the local wheel. Node was
extracted from its tarball, with every archived file checked against the actual
application files; its locked dependencies were copied into the container from
the prepared installation. This matrix is execution evidence; the separate
[clean installation walkthrough](../../../docs/quickstart.md) explains adopter
setup. Exact image, installed file, dependency, specification, schema, fixture
and harness identities are in the report. Sources and installed artifacts
remained unchanged during the run.

[evidence.zip](evidence.zip) retains all 3,493 per-case files: received and edited
fixtures, digest inventories, public CLI output, provider audits, run reports,
raw result artifacts and engine logs. Its SHA-256 and a file digest manifest
are recorded. Extract it beside `report.json` to resolve the report's case paths.
The suite invokes actual public CLIs, checks observed quantities independently,
correlates call artifacts and provider audits, and rejects success inferred from
schema validity or engine exit alone.

Evidence includes missing providers and revisions, explicitly authored provider
replacement, malformed CWL/default inputs, partial failures, unknown mutation
outcomes without replay, incompatible units and finite numeric overflow.
The two applications have distinct readers, resolvers and adapters. They share
the published schemas/fixtures and some upstream CWL parsing libraries. Real
Solid Edge execution, native-save/export failures, real CAD mutation
reconciliation and authorized human approval remain **not run**, with explicit
prerequisites in the report. HTTP evidence uses actual loopback networking with
controlled mock platform metadata; it does not establish authenticated or
cross-platform CAD interoperability. This is a finite experimental demonstration,
not a stable-standard or certification claim.

The [earlier diagnostic summary](diagnostic-report.json) preserves tested
identities and failures that led to stricter job/unit validation and corrected
CLI status handling. The [fixture diagnostic summary](fixture-diagnostic-report.json)
records an overflow test whose first input mistakenly omitted required CWL
record members: cwltool rejected it while StreamFlow executed it. The corrected
suite preserves those members, adds explicit invalid-record cases, and both
readers now reject missing members and wrong types before execution. Numeric
conversion overflow returns indeterminate acceptance with finite evidence.
These earlier summaries are historical diagnostics, excluded from the final
pass totals; their transient per-case paths are not the final archive's paths.
