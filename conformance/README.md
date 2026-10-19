# Proposed conformance and interoperability plan

**Status:** proposed acceptance plan, not a certification suite. This repository
contains documentation and evidence references; it does not yet ship a second
parser, validator or executor. No current implementation receives a conformance badge.

## Claim only the role actually tested

| Role | Minimum proposed claim |
|---|---|
| Package reader | Recognizes an exact profile/version, checks declared integrity, inventories dependencies and reports unsupported requirements |
| Preserving editor | Round-trips supported meaning and retains unsupported content without silent loss; explicit edits expose conversions |
| Importer | Creates a fresh local definition without overwriting work, adopting permissions or silently changing defaults |
| Executor | Executes a declared subset with compatible providers, correct handoffs, local readiness, evidence and declared interaction/recovery |
| Optional UI host | Binds presentation to the executor's exact subjects, checks compatibility and provides fallback |

A Wright desktop panel talking to Wright is another host, not a second executor.
Two workspaces prove transfer within one implementation. Two models using the
same runner also do not establish independent execution.

## Required vectors before claiming the first interoperable subset

| ID | Scenario | Expected outcome | Draft clauses |
|---|---|---|---|
| C01 | Export → import → export without editing | Source/instructions/assets preserved under the profile's exact equality rules; local storage/run IDs not reused | P01–P04 |
| C02 | Unicode, finite numbers, negative zero, exponent notation and line endings | Independently computed digests match declared canonicalization/byte vectors, or unsupported values are rejected | P04 |
| C03 | Required provider absent or unavailable on recipient platform | Definition remains inspectable/preserved; readiness identifies affected blocks; no silent replacement | P05–P06 |
| C04 | Same tool name/schema from a different implementation | No inferred provider equivalence; explicit qualification or edit required | P05 |
| C05 | Missing/tampered reference, instruction or pinned validation profile | Integrity/closure failure before executable acceptance; exact diagnostic | P08–P09 |
| C06 | Recipient has different AI defaults/model configuration | Embedded instructions unchanged; model requirement/substitution resolved visibly before execution | P09–P10 |
| C07 | All deterministic steps, no model configured | No artificial AI requirement if the supported dialect needs none | P10 |
| C08 | Initial input, upstream-produced value and declared later question | Correct readiness classification and same-run wait/resume; invalid/stale answer does not advance | P07, P11 |
| C09 | Conditional input has fully resolved versus unresolved fields | Record skip versus ask from the exact typed evidence; never invent answer fields | P11 |
| C10 | Old artifact/source/profile after a decision | Affected check/review is stale; prior evidence remains accessible | P12–P14 |
| C11 | Required check unavailable or measured value fails | Preserve measurement/finding and hold affected downstream action | P12 |
| C12 | Bounded rework exhausted or crosses answered input | Apply declared failure/hold policy without expanding scope or replaying the answer | P14 |
| C13 | Submission accepted, completion unknown, then reconnect/cancel | Keep separate facts; reconcile exact action; no automatic resubmission or inferred physical stop | P15 |
| C14 | Missing/incompatible UI or closing/reopening a tab | Common view remains usable; exact run is reattached without replay | P16–P17 |
| C15 | Attempt to include grants, prior answers, secrets or trusted UI build | Reject prohibited authority/configuration; no new local permissions or run created | P18 |
| C16 | Interrupted import, lost reply or existing destination | Preserve existing/partial files, read state, block uncertain replay; reservation is not completion | P19 |
| C17 | Unknown required dialect/extension | Unsupported diagnostic; preserve opaque original where supported, never falsely claim execution support | P02 |

C15 does not imply a generic secret detector can recognize every sensitive string
inside arbitrary asset bytes. Content selection and local security policy are
separate from schema/authority exclusion.

## First qualification sequence

1. Freeze a profile, representative packages and exact expected diagnostics.
2. Build an independent reader/round-tripper without importing Wright's parser.
3. Define the supported execution subset and run the [engineering cases](../use-cases/README.md)
   in Wright and the independent executor with qualified access to the same providers.
4. Add negative controls for absent providers, changed schemas/resources, unmet
   checks, stale decisions and uncertain operations.
5. Publish a per-role/per-case report, including unsupported behavior and failed
   attempts. Extend the subset only after new implementation evidence.

A report records implementation/commit, profile/version, environment, package and
input hashes, resolved provider/resource/model identities, expected versus observed
behavior, exact output/evidence identities and limitations. Existing Wright tests
are seeds for vectors, not substitute independent-implementation evidence.

Do not execute physical actions or adopt historical review authority to qualify
format exchange. Use isolated digital cases and genuine separately authorized
review where required. Existing protected engineering campaign evidence stays intact.
