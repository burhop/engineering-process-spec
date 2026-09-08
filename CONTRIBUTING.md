# Contributing to the experimental draft

This repository develops an experimental process specification and implementer
kit. Start with the [vision](VISION.md), [repository instructions](AGENTS.md),
[goal audit](docs/goal-audit.md) and [maintenance rules](docs/maintenance.md).
Current examples and tests support only their stated profiles and versions.
External contribution, licensing and contributor-IP terms remain undecided;
this document does not select those terms or authorize publication.

## Make one reviewable change

1. Describe the concrete process or implementation problem, expected behavior
   and affected requirement IDs. For a larger semantic change, add a short
   decision proposal with alternatives, compatibility impact and an example.
   Small corrections need a concise change description, not a new committee.
2. Update the relevant requirements, schemas, semantic validation, examples,
   expected observations and adopter instructions together. Preserve old
   evidence; identify the new draft and implementation revisions it tests.
3. Run the applicable checks once implemented. Record exact commands and their
   results, including unsupported or unrun cases and their reasons. The
   [check interface](docs/maintenance.md#checks-and-evidence) currently identifies
   pending commands; a placeholder is not a passing check.
4. Request review of the resulting behavior and evidence. Explain limitations
   and unresolved decisions. Pure editorial changes need appropriate document
   checks, rather than invented behavior tests.

For new standards or implementation claims, follow the
[research brief](RESEARCH.md) and [source-register policy](research/sources.md):
use authoritative sources, exact versions/revisions and access limitations.
Distinguish specifications, inspected source, recorded execution and proposals.
Do not mirror inaccessible standards or infer their contents.

## What reviewers check

- A named provider remains that provider. Local rebinding does not change the
  process; provider replacement is an explicit, validated process revision.
- Unavailable dependencies and unknown semantics are preserved and diagnosed.
  Opening a process performs no engineering calls. Execution, partial output,
  acceptance and approval remain distinct.
- Required behavior is clear to an implementer without Wright or conversation
  history, and maps to meaningful tests. Schema validity alone is insufficient.
- Claims name the tested role/profile, implementations and versions. Mocks,
  unrun CAD tests and shared execution components are disclosed.
- Upstream material retains required notices; project license/IP terms have not
  been chosen by a code header, dependency update or contribution instruction.

Keep Wright read-only: no modifications, launches or Wright test runs for this
work. An external compatibility adapter belongs here and takes explicit inputs.
Do not change visibility, publish packages/releases, contact third parties or
claim stable standardization under the implementation goal. Record proposed
later actions in the [readiness gates](docs/maintenance.md#readiness-gates).
