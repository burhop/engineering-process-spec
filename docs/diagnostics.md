# Diagnose a process without changing its meaning

Diagnostics include `code`, `category`, normative `requirement`, `message` and,
where available, a node/dependency/pointer, expected/observed values and native
cause. Keep those facts when presenting a friendly message. Human-readable text
is not a stable parsing interface. Use `category` plus `requirement` to compare
implementations; detailed codes below identify their current local causes.

| Category | Meaning | Appropriate application response |
|---|---|---|
| `invalid` | A known structural or semantic rule is violated | Retain original material; show the author the exact violation for an intentional correction |
| `unsupported` | Required meaning/version or bounded reader feature is not implemented | Preserve it; decline affected interpretation/execution; identify the missing support |
| `unavailable` | Intended provider, version, platform, credentials or resource cannot be verified/accessed | Preserve the valid supported definition; configure the intended dependency or let the user explicitly edit a replacement |
| `execution-failed` | An invoked operation or required output failed with known evidence | Retain native causes and successful upstream results; evaluate only available valid evidence |
| `outcome-unknown` | A submitted mutation may have happened but its outcome is unverified | Retain uncertainty; require inspection and an explicit recovery decision before any retry |

## Common causes

This is a concise catalog, not a restriction on useful provider-native detail.
Python code names are shown first; representative Node counterparts follow.

| Cause and representative codes | Requirement | Evidence/action |
|---|---|---|
| `JSON_INVALID` / `EPX_JSON_INVALID` | PKG-001 | Malformed JSON, duplicate keys or nonfinite numbers; correct explicitly, retaining received bytes |
| `PACKAGE_PATH`, `PACKAGE_DUPLICATE_MEMBER` / `EPX_PATH_INVALID`, `EPX_ZIP_DUPLICATE` | PKG-001 | Escaping/ambiguous archive member or symlink; do not materialize it outside the package |
| `CRATE_INVALID`, `CRATE_PARTS` / `EPX_CRATE_INVALID` | PKG-002 | Inventory/root/profile relationships are inconsistent |
| `PAYLOAD_DIGEST_MISMATCH` / `EPX_PAYLOAD_DIGEST_MISMATCH` | PKG-002 | Expected and observed bytes differ; do not silently refresh a received inventory |
| `FEATURE_UNSUPPORTED` / `EPX_FEATURE_UNSUPPORTED`, `EPX_PROFILE_UNSUPPORTED` | PKG-003, CORE-003 | Unknown required feature/profile; human-approval example intentionally reaches this state |
| `NODE_MAPPING`, `INVOCATION_MAPPING` / `EPX_OPERATION_INVALID`, `EPX_INVOCATION_MISMATCH` | CWL-003 | Graph node, fixed binding/tool arguments or operation manifest disagree |
| `DATA_REFERENCE`, `DATA_CYCLE` / `EPX_HANDOFF_INVALID`, `EPX_CYCLE_INVALID` | CWL-005, CWL-001 | Missing port/input or cyclic dependency; schema validation alone cannot resolve it |
| `ENGINE_UNAVAILABLE`, `ENGINE_VERSION` / `EPX_ENGINE_UNAVAILABLE`, `EPX_ENGINE_VERSION_MISMATCH` | CWL-001, CORE-003 | Install/configure the exact tested engine; an unknown installed version is not an automatic upgrade |
| `PROVIDER_UNAVAILABLE`, `PROVIDER_IDENTITY_MISMATCH` | BIND-001, BIND-005 | Missing receiving binding or a different intended implementation/application; same tool name is insufficient |
| `IDENTITY_EVIDENCE_MISSING`, `LAUNCHER_IDENTITY_MISMATCH`, `SERVICE_TRUST_MISSING` | BIND-002 | Configured connection does not establish the intended provider identity |
| `PROTOCOL_MISMATCH`, `PROVIDER_METADATA_MISMATCH` | BIND-003 | Negotiated protocol or observed application/version differs, including a changed default |
| `TOOL_UNAVAILABLE`, `TOOL_CONTRACT_MISMATCH` | BIND-004 | Intended server lacks the named tool or its captured schema changed |
| `RESOURCE_UNAVAILABLE`, `RESOURCE_REVISION_MISMATCH` | RES-001, RES-002 | Resource is absent, denied, ambiguous or a different revision; inspect native cause without inventing deletion |
| `TOOL_ERROR`, `MCP_RPC_ERROR`, `TOOL_RESULT_INVALID` / `EPX_TOOL_ERROR`, `EPX_OUTPUT_INVALID` | OUT-003 | Distinguish tool `isError`, JSON-RPC error and output-schema failure |
| `MUTATION_OUTCOME_UNKNOWN` / `EPX_MUTATION_OUTCOME_UNKNOWN` | RES-003 | A submitted mutation lost its response; no implicit rollback or automatic replay |
| `ENGINE_EXECUTION_FAILED` / `EPX_REQUIRED_OUTPUT_MISSING`, `EPX_ENGINE_OUTPUT_INVALID` | OUT-003, CWL-005 | Exit status does not establish exactly the declared successful calls and required materialized outputs |

Schemas reject malformed field shapes; semantic validation catches inconsistent
references and unsupported meaning. Preflight may start a provider session for
discovery and resource reads, but makes zero engineering `tools/call` requests.
Opening/validation/preservation makes no provider call at all.

## Read the run report

Check `execution.status`, then each acceptance criterion and its reason/evidence.
`fail` means a performed criterion did not pass. `not-run` means required
successful evidence was absent. `indeterminate` means the evidence could not
establish the criterion, for example a mismatched digest or unsupported unit.
None can be promoted to `pass` because another criterion passed.

Partial results keep their original identities and durability. A failed STEP
export must not erase an earlier native result or certify the missing export.
An MCP transport response is separate from the tool result's `isError` field.
An engine may exit `0` after a task failure; the driver must inspect declared
outputs and call evidence too. Human approval is always separate and is outside
this core's executable scope.

Python CLI exit `0` means the requested operation completed successfully; `1`
indicates invalid input, `2` another rejected readiness/support condition, and
`3` a run without both successful execution and passing acceptance. Node CLI
returns nonzero on rejection; parse its JSON rather than assuming identical
numeric codes. Always retain the report for failed or uncertain runs when one
was produced. See [quickstart](quickstart.md) for an actual missing-binding case.
