# Compatibility and claim boundaries

Use the exact artifact/source identities in the
[conformance report](../conformance/README.md) and
[installed-consumer evidence](adopter-evidence.json) for a tested claim.
Version equality is intentional in this draft; newer is not implicitly compatible.

| Layer | Python path | Node path | Boundary |
|---|---|---|---|
| Exchange core | `engineering-process-kit 0.1.0.dev1` | `epx-node-adopter 0.1.0-draft.1` | Profile `urn:engineering-process-spec:core:0.1.0-draft.1`; package versions and profile versions are distinct |
| Reader and limited editor | Python implementation | Independent JavaScript implementation | Directory/ZIP preservation, core structure/references, explicit same-contract provider revision; no general CAD translator |
| Workflow execution | cwltool `3.2.20260720092025` | StreamFlow `0.2.0rc2` | Packed CWL v1.2 JSON fixed-call core; specification/test revision 1.2.1; full upstream suites are not claimed here |
| Binding and MCP adapter | Python standard-library protocol client | Independent Node protocol client | MCP `2025-11-25`, stdio and Streamable HTTP JSON responses; fixture identity/resource checks; no complete MCP SDK claim |
| Structural data schemas | jsonschema `4.26.0` in the tested engine image | Ajv `8.18.0` | Shared Draft 2020-12 schemas; separate semantic checks |
| Execution environment | Python `3.12.14`, Linux/amd64 | Node `24.13.1`, Linux/amd64, invoking installed StreamFlow | Docker supplies the recorded environment; Windows reader/preflight checks do not prove native Windows CWL execution |
| Named provider | Explicit `engineering-process-mock` fixture | Same exact declared fixture, independently bound | Mock calculation, resource and mutation behavior; never Solid Edge |
| HTTP platform case | Real loopback HTTP | Real loopback HTTP | Controlled execution-target metadata tests target/client separation; does not prove a real cross-OS CAD deployment |
| Wright source | External byte-preserving capture | No Wright parser/runtime import | `.wflow` is not already conforming; see [versioned mapping](wright-compatibility.md) |
| Human approval / real CAD | Not implemented / not run | Not implemented / not run | Preserved approval case and authentic Solid Edge capture plan; separate readiness gates |

The binders, protocol clients, acceptance code and runtime drivers are separately
implemented. The existing engines have different scheduling/execution code but
share lower-level Python/CWL parsing libraries, including cwl-utils and
schema-salad. The [baseline experiment](../experiments/workflow-baseline/README.md)
records that scope. This is implementation independence at the stated layers,
not an independent organization adopting the draft.

The initial HTTP implementation is deliberately bounded. SSE streaming,
resumable MCP sessions/tasks, authorization provisioning, automatic recovery,
distributed compensation and signed executor attestation need separate evidence
and explicit profiles. Credentials and local connection/trust configuration
remain receiving-application responsibilities.

Preserving an unsupported package is a reader operation. It does not make the
unsupported feature executable. A missing provider is an availability condition;
same-named tools from another provider do not satisfy it. A failed or uncertain
run retains partial evidence without becoming accepted or approved.
