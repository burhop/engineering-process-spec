# Decision 003: experimental CWL execution core

Status: implementation decision for the experimental draft, 2026-09-07.
This selects an experiment-backed baseline; it is not a stable standard claim.

## Decision and evidence

Use CWL v1.2 as the executable representation, with the 1.2.1 specification/test
revision identified separately. Profile ordinary Workflow and CommandLineTool
documents; implement named MCP invocation through a required adapter contract.
Keep orchestration in existing CWL engines.

The bounded experiment in `experiments/workflow-baseline/` built Synapse at
`ba3fbfd5125995bba9fb5900aed181a0775d538c` and exercised its control and MCP paths.
Its MCP call was routed to an unsupported function. Inspected Java runtime
handlers also did not provide MCP execution. This is evidence about those
versions, not a claim about all possible OWS implementations. A zero process
exit status did not establish successful Synapse execution; logs/results matter.

The same two-step CWL file executed on cwltool `3.2.20260720092025` and StreamFlow
`0.2.0rc2`, yielding matching JSON handoff receipts. StreamFlow has its own
scheduling/execution path; the inspected release has no runtime cwltool imports.
Shared cwl-utils/schema-salad components must be disclosed. The retained
experiment report supplies exact image/source identities and commands.

This proves the bounded workflow-engine handoff only. MCP, provider preservation,
resource checks, error handling and acceptance still need profile tests on both
independent adapters before any core conformance claim.

## Frozen minimum core

The draft core includes fixed named MCP calls, explicit CWL data handoff, the
deterministic quantity calculation, preservation, intended provider/resource
binding, failure and partial outcomes, and acceptance evidence. Both execution
paths must pass all mandatory core tests; a calculator-only result is insufficient.

The portable profile defines how to consume required exchange metadata and bind
the MCP command adapter. It does not replace CWL graph semantics with another
interpreter. Its two adapters must not share the provider resolver, protocol
client or outcome implementation. Reused engines/parsers and standards are
reported by layer rather than described as wholly independent software stacks.

## Consequences

CWL's batch boundary fits the first calculation and fixed-call MCP examples.
Stateful CAD resources require explicit identity/revision handling in the adapter.
Human approval and AI-directed task execution remain separate profiles and
must not be represented as an equivalent fixed-call conversion.

OWS remains a useful upstream reference and a future alternative if independently
implemented MCP support improves. Reconsidering the baseline requires a new
versioned decision and interoperability evidence, not a silent file conversion.
