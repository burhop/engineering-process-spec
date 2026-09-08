# Implementation review — 2026-09-07

This review checks the experimental core, adopter documentation and
`IMPLEMENTATION_GOAL.md`. It is not a conformance report. Final execution claims
must cite the matching implementation/test identities and retained reports.

## Remaining boundaries

- **Wright conversion remains unimplemented.** The external
  [capture utility](../tools/wright_capture.py) preserves explicitly supplied
  originals and reports missing facts. It does not parse `.wflow`, validate the
  recovery canonical schema, verify supplied provider facts or produce a
  conforming export. The observed CAD fixture was captured without canonical
  context or an authoritative binding-fact file. The
  [compatibility mapping](wright-compatibility.md) identifies the facts and
  semantic mapping needed before a conversion can be tested.
- **Real Solid Edge portability remains an evidence gate.** A source repository
  identity, historic trace or matching tool schema does not pin a deployed
  provider artifact or establish access to the intended model revision. A real
  provider needs verified identity, contract/resource evidence and a documented
  adapter for the profile metadata. The mock handoff demonstrates protocol and
  evidence handling; it does not establish CAD correctness or certify another
  product as an equivalent replacement.
- **Reader validity is scoped to this core.** The supported representation is
  packed CWL JSON with one named workflow and fixed MCP adapters. Readers check
  the declared profile's structure and cross-references; upstream engines remain
  responsible for complete CWL parameter/expression validation at execution.
  Supporting this profile does not make either reader a general CWL validator.
- **Independent implementations are not independent organizations.** The Python
  and Node receiving paths use separately written binding/adapter logic and
  different existing engines, with shared schemas and fixtures. Their eventual
  passing reports establish only their tested roles and cases. An outside
  implementer and a verified real-CAD transfer are subsequent adoption evidence.

## Review corrections

The review found a Node CLI bug where successful `inspect`/`validate` output
returned exit code 1 because unevaluated acceptance criteria were mistaken for
a run verdict. Both commands now have subprocess regression checks. It also
demonstrated that an unknown unqualified CWL property could pass reader checks
while the pinned upstream engine rejected it. The core's known field checks
now reject that case; namespaced optional metadata remains preserved.

A later numeric review reproduced two acceptance errors with finite `1e308`
measurements: converting kg to g produced infinity, serialized as `null`, and
same-unit g/cm3 comparison overflowed unnecessarily before dividing back. Unit
conversion now multiplies by the precomputed unit ratio and marks an
unrepresentable converted value `indeterminate`. Focused tests first failed
against the prior code and now verify both corrected outcomes with retained,
hashed test evidence. These arithmetic tests do not claim real provider runs.

The execution checks also exposed an engine difference: a default job omitting
required quantity-record fields was rejected by cwltool but executed by
StreamFlow. The independent readers now check the declared default job's CWL
record fields and scalar types before preflight, preserving source while
rejecting invalid values. Node regression tests cover missing quantity/unit,
wrong scalar type, nested records/arrays/enums, nullable fields and parameter
defaults without rewriting the job.

The readers and examples were aligned with required RO-Crate descriptor/root
metadata. The draft explicitly selects day-precision `YYYY-MM-DD`; upstream
RO-Crate also permits other ISO 8601 precision. Its textual license metadata
option allows the examples to state that licensing terms remain undecided,
without granting or selecting terms. [RO-Crate 1.2 root requirements](https://www.researchobject.org/ro-crate/specification/1.2/root-data-entity.html).

## npm audit triage and resolution

The initial installed consumer reported four moderate records: three underlying
advisories and one derived `epx-node-adopter` dependency record. The application
itself had three affected dependency entries. The final dependency state below
was checked with `npm audit --omit=dev --json`, which reported **zero findings**;
this is the advisory database result at the observation date, not a general
security certification.

| Previous dependency / advisory | Observed exposure in this application | Resolution |
|---|---|---|
| Ajv 8.17.1, [GHSA-2g4f-4pwh-qvx6](https://github.com/advisories/GHSA-2g4f-4pwh-qvx6) | The reported dynamic-pattern path requires `$data: true`; the application's Ajv constructor does not enable that option. | Pin **8.18.0**, the minimum reported patched version; the [upstream release](https://github.com/ajv-validator/ajv/releases/tag/v8.18.0) identifies the change. |
| yaml 2.8.1, [upstream GHSA-48c2-rrv3-qjmp](https://github.com/eemeli/yaml/security/advisories/GHSA-48c2-rrv3-qjmp) | A 10,001-byte nested collection reproduced `RangeError` in the old parser. The public loader caught it and returned an invalid-package diagnostic; an unhandled application crash was not demonstrated. | Removed the unused dependency when the core was explicitly restricted to packed CWL JSON. Upstream's minimum patched version is 2.8.3. |
| yauzl 3.2.0, [GHSA-gmq8-994r-jv83](https://github.com/advisories/GHSA-gmq8-994r-jv83) | The affected NTFS timestamp path requires `entry.getLastModDate()`. The importer does not call it, and the inspected library does not call it internally. | Pin **3.2.1**; the [upstream change history](https://github.com/thejoshwolfe/yauzl/commit/c469521) records the corrupted-timestamp fix. |

The patched Node source passed 15 unit tests, including public CLI, preservation,
replacement and actual engine-output evidence checks. Its final local tarball
SHA-256 is
`84f5d664992274ae7d6c65433f7f386f96ea4aa4c8209d2461d6d96d07258843`.
The full interoperability suite and copied-artifact walkthrough are separate
evidence and must use that artifact or identify any subsequent change.
