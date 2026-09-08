# Deterministic mock MCP provider

This test-only provider implements a bounded MCP **2025-11-25** interaction over
stdio and loopback Streamable HTTP. It has no Wright, CAD, model API, credential
or third-party Python package dependency. It is **not Solid Edge**, an engineering
solver, a general unit library or a certified MCP implementation.

Use Python 3.10 or later from the repository root. The retained
[protocol report](protocol-results.json) identifies the exact tested interpreter,
platform, commands and source/snapshot hashes. Tests require no internet access;
HTTP tests create temporary loopback listeners and terminate them afterward.

```text
python tests/providers/test_mock_mcp.py --report tests/providers/protocol-results.json
python tests/providers/snapshot_contract.py
```

The protocol suite exercises a real subprocess and actual JSON-RPC messages.
Its 25 cases cover both transports, lifecycle, discovery, calculations, schema
snapshots, resource identity, controlled errors and mutations. These tests verify
the mock's behavior, not the independent clients' binding decisions or real CAD
interoperability. A deliberate malformed-output fault is intentionally outside
the declared tool output schema.

## Start and connect

For a stdio client, launch this executable and argument array:

```text
python -u tests/providers/mock_mcp_server.py
```

Send one UTF-8 JSON message per line. Initialize with protocol version
`2025-11-25`, `capabilities: {}` and a client name/version, then send
`notifications/initialized`. Supported requests are `ping`, `tools/list`,
`tools/call`, `resources/list`, `resources/read` and an empty
`resources/templates/list`. No tasks, SSE, subscriptions, pagination continuation,
sampling or prompts are advertised. Notifications receive no stdio response.
Close stdin to stop the server; stdout contains only protocol messages.

For the controlled remote-binding scenario:

```text
python -u tests/providers/mock_mcp_server.py --http-port 0 --execution-platform mock-linux-target
```

The listener binds only `127.0.0.1`; port `0` selects a free port. One readiness
JSON line on stderr reports `event: "listening"`, its `/mcp` URL and protocol
version. HTTP mode writes nothing to stdout. The platform override changes
mock metadata; it does not establish real Linux execution or vendor support.

POST JSON to `/mcp` with `Content-Type: application/json` and an `Accept` header
containing both `application/json` and `text/event-stream`. Initialization returns
`Mcp-Session-Id`; echo it and `MCP-Protocol-Version: 2025-11-25` on subsequent
requests and notifications. Responses use JSON; accepted notifications return
empty HTTP 202. GET returns 405 because this subset does not open SSE streams.
DELETE with the session/version headers terminates that session. Unknown or
deleted sessions return 404; incompatible protocol headers return 400.

Each HTTP session has separate mock state. Multiple HTTP connections can use
the same session; there is no parallel task execution. This unauthenticated
loopback fixture is for controlled tests. It is not a deployment example for a
trusted remote engineering service.

## Identity and tool contract

Normal initialization returns `serverInfo.name: "engineering-process-mock"` and
`version: "0.1.0-draft.1"`. Initialization and `tools/list` include the same
experimental declaration at `_meta["engineering-process-provider"]`:

```json
{
  "implementation": "urn:engineering-process-spec:mock-mcp",
  "revision": "0.1.0-draft.1",
  "application": "urn:engineering-process-spec:mock-engineering",
  "applicationVersion": "0.1.0-draft.1",
  "executionPlatform": "<Python sys.platform, unless explicitly overridden>"
}
```

The metadata key uses MCP's permitted unprefixed syntax; a URN containing colons
is not a valid `_meta` key. These URNs and fields belong to this local experimental
fixture. This is not a standardized MCP provider-identity extension. The
declaration alone does not authenticate an implementation. A client may verify
the launched script's exact bytes; HTTP trust and provider matching need their
own application policy and conformance tests.

| Tool | Inputs | Normal structured output |
|---|---|---|
| `engineering.volume` | Positive finite `length`, `width`, `thickness`, each `{value, unit}` with `m` or `mm`; optional `quantity: "length"` | `{quantity: "volume", value: 0.00002, unit: "m3"}` for 100 × 80 × 2.5 mm |
| `engineering.mass` | Positive finite `volume` in `m3`/`mm3` and `density` in `kg/m3`/`g/cm3`; optional matching quantity meanings | `{quantity: "mass", value: 0.157, unit: "kg"}` for the example volume and 7850 kg/m3 |
| `engineering.record` | `measurement: {quantity, value, unit}`; finite mass/volume/length/thickness with the supported matching unit | `{stored: true, measurement: ..., resource: {id, provider, revision}}` |

Mass accepts the complete volume output directly. Normal results include both
`structuredContent` and its serialized JSON as a text content block. The
calculation implements only the listed conversions. Invalid dimensions, values,
unknown input fields and unsupported units yield `isError: true`; a malformed
request or unknown tool yields a JSON-RPC error. Non-JSON `NaN`/`Infinity`,
unrepresentable input numbers and non-finite computed results are refused.

Each tool's reviewed descriptor, input schema and output schema are separate
files in [snapshots](snapshots). The schemas use JSON Schema 2020-12. Runtime
checks cover these fixed tool contracts; this server is not a generic schema
validator. `snapshot_contract.py` checks snapshot bytes without changing them.
After reviewing an intentional contract change, explicitly regenerate with:

```text
python tests/providers/snapshot_contract.py --write
```

## Resource, mutation and audit evidence

`resources/read` for `mock://plate` returns one JSON text resource containing
`id`, mock application `provider`, `revision: "r1"`, the example dimensions and
density. Repeated reads before mutation are identical. Recording a measurement
stores it in memory and increments the resource revision to `r2`, then `r3`, and
so on. Recording the same measurement twice still creates two revisions;
`engineering.record` is deliberately not idempotent.

State and revisions are scoped to the stdio process or HTTP session. They are
not durable cross-session resource identities. A new session starts with the
initial plate; this cannot demonstrate portable CAD document lifetime.

Optionally append actual request/tool-call and mutation events to an explicit
audit path whose parent directory already exists:

```text
python -u tests/providers/mock_mcp_server.py --audit tests/providers/local-audit.jsonl
```

Events distinguish `request`, `tool_call`, `resource_read`, `mutation` and
`disconnect_after_mutation`. Each includes a session label and local sequence.
Mutation evidence is flushed to the audit file before the deliberate disconnect.
Absence of `tool_call` demonstrates no engineering tool was invoked during the
observed session; it does not prove behavior outside that trace. The audit is
test evidence, not a process artifact or durable resource service.

## Controlled negative cases

Fault controls are command-line configuration, never accepted tool arguments.
`--fault-tool` limits tool faults to one named tool, allowing volume to succeed
before mass fails. Without it, the fault applies to matching tool calls.

| CLI option | Controlled observation |
|---|---|
| `--fault tool-error` | Tool result has `isError: true` |
| `--fault rpc-error` | JSON-RPC error `-32603` |
| `--fault malformed-output` | Successful envelope contains structured content outside the advertised schema |
| `--fault wrong-unit` | Calculation returns unit `s` instead of its advertised unit |
| `--fault wrong-value` | Calculation returns 1000 times the computed result while retaining the expected quantity/unit |
| `--fault disconnect-after-mutation --fault-tool engineering.record` | Mutation is recorded, then the connection closes without a call response; no automatic replay occurs in the server |
| `--application urn:engineering-process-spec:mock-other-engineering` | Initialization and discovery consistently advertise another mock application |
| `--fault changed-default` | Discovery changes the application after initialization; the mismatch is observable before calls |
| `--resource-state absent` | Resource is absent from enumeration and read returns `-32002` |
| `--resource-state denied` | Read returns this mock's `-32003` with reason `denied`; that code is not a universal MCP permission code |
| `--resource-state revision-mismatch` | The initial resource reports `r999` instead of `r1` |
| `--execution-platform NAME` | Explicit controlled target-platform declaration independent of the client OS |

After an HTTP disconnect fault, the original session remains readable for
explicit recovery inspection. A stdio disconnect ends that process; only its
audit remains. Neither behavior authorizes a client to replay a possibly applied
mutation. Input and frame limits are bounded for this fixture; by default a
session refuses tool execution after 256 calls.

## Authoritative sources and limits

Protocol behavior was checked on 2026-09-07 against official MCP **2025-11-25**
[lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle),
[transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports),
[tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools),
[resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources),
[general fields](https://modelcontextprotocol.io/specification/2025-11-25/basic/index#meta)
and [ping](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/ping).
The corresponding [TypeScript schema at revision e76e9c572c6f2bfcb730357101acc90f2f802e02](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/e76e9c572c6f2bfcb730357101acc90f2f802e02/schema/2025-11-25/schema.ts)
was inspected for message structures, including error responses with omitted
unknown request IDs. No SDK, Wright runtime or upstream schema implementation
was copied into this provider. The tool schemas describe newly authored mock
operations; they are not vendor schemas.

The protocol report is local observed evidence for this subset. It is not an
official MCP conformance-suite result, an authentication proof, a complete
JSON Schema validator test, an engineering acceptance report or a claim about
MCP 2026's changed lifecycle. Project licensing remains undecided; linking
upstream specifications does not select the project's terms.
