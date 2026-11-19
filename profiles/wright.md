# Wright implementation profile

**Reviewed 19 November 2026.** This profile describes the standalone `wright-workflow` development version `0.1.0.dev2`. An implementer can use its public parser, schemas and executable example to check their interpretation of a file. The interchange requirements remain a draft. [Wright source and quickstart](https://github.com/burhop/wright/tree/85f97930927b672ddf7da8cc65e89569236f4f44#run-the-example) · [Interchange draft](../spec/interchange-draft.md)

## Identify the document

| Representation | How to read it |
| --- | --- |
| Native source, `.workflow.wflow` | UTF-8 text with named sections. Compute `source_digest` as SHA-256 of the exact source bytes, including comments and line endings. |
| Definition bundle, `wright.workflow-bundle/1` | JSON with `schema_version`, `mode`, `source` and `source_digest`. Check the digest of the source string encoded as UTF-8 and validate the declared dependencies. |
| Export wrapper | A JSON object containing exactly `bundle` and `bundle_digest`. Verify the digest over Wright’s canonical structured representation of the validated bundle. Whitespace in the outer JSON and whitespace inside the source string have different significance. |

Both `source` and `bundle` are envelope modes. The source mode carries source and dependency declarations. Bundle mode can also carry selected file assets and editable interface source. The schema defines fields for layout, assets, dependencies and interfaces. Source-level checks also compare the inventory with the requirements derived from the source. The envelope version, MCP binding version and software version identify different things. [Bundle schema](https://github.com/burhop/wright/blob/85f97930927b672ddf7da8cc65e89569236f4f44/src/wright_workflow/schemas/workflow-bundle-1.schema.json) · [Parser and digest checks](https://github.com/burhop/wright/blob/85f97930927b672ddf7da8cc65e89569236f4f44/src/wright_workflow/definition.py)

## Read a connection

The source uses `workflow`, `task`, `input`, `item`, `group` and `connection` sections. Here is the complete connection from the two-provider example.

```text
connection coordinates_to_reader
  type: "item"
  from: "writer.coordinates"
  to: "reader.source_file"
  label: "Coordinate file"
  when: null
end
```

`writer.coordinates` identifies one named output. The reader consumes the file from that port and reports a length of 5 mm. An `order` connection constrains ordering. A `group` records layout. Wright’s graph compiler currently accepts one connected workflow with 1–32 tasks. That limit belongs to this implementation. [Complete source](https://github.com/burhop/wright/blob/85f97930927b672ddf7da8cc65e89569236f4f44/examples/handoff/length.workflow.wflow) · [Source grammar and supported constructs](https://github.com/burhop/wright/blob/85f97930927b672ddf7da8cc65e89569236f4f44/FORMAT.md)

## Bind the intended MCP tool

A fixed-call task selects its logical server and operation. Its portable `mcp_binding` record identifies the version (`wright.mcp-binding/1`), provider, build, upstream tool and `contract_sha256`. The contract digest covers the tool name, input/output schemas and any reported annotations, metadata or execution declarations included by the profile.

The writer in the example declares this exact `mcp_binding` value.

```json
{
  "version": "wright.mcp-binding/1",
  "provider": "example-write_points",
  "build": "1.0.0",
  "tool": "write_points",
  "contract_sha256": "27ed9e6381d5e3b3164cc2b200b74603a76197523dfaf1a9215700b32bbcbfc4"
}
```

The receiving user separately supplies local bindings with absolute executable paths, arguments, reviewed file hashes and permitted tools. Wright starts the configured stdio provider and compares the reported provider/build and tool contract with the declaration. A historical `mcp_schema_digest` has its own meaning that includes local server identity and approval metadata. Preserve its interpretation when reading older definitions. [Binding model and qualification](https://github.com/burhop/wright/blob/85f97930927b672ddf7da8cc65e89569236f4f44/src/wright_workflow/bindings.py) · [Example binding generator](https://github.com/burhop/wright/blob/85f97930927b672ddf7da8cc65e89569236f4f44/examples/handoff/configure.py)

## Separate reading, readiness and execution

| Stage | What Wright demonstrates |
| --- | --- |
| Inspect | `wright-workflow parse` returns the source digest, ordered blocks, ports, required features and dependencies without contacting a provider. |
| Prepare | The caller supplies inputs and local bindings. A well-formed definition can require a handler or provider that this installation lacks. Unsupported required behavior and changed contracts block the affected execution. |
| Execute | Fixed MCP calls can pass verified files and structured values through named ports. The run receipt records attempts, produced outputs and consumed inputs. |
| Continue | At a declared human input, `waiting_input` includes the subject and value schema. A matching response can continue the same run. A lost response to a dispatched call can leave `outcome_unknown`, with its attempt retained for reconciliation. |

The example exercises one implementation through two separate MCP servers. Independent-reader round trips, cross-language digest agreement and execution by a second implementation remain separate interoperability milestones. The wider authoring, validation, review and interface contracts examined in October remain documented as historical evidence. [Runnable CLI and Python examples](https://github.com/burhop/wright/blob/85f97930927b672ddf7da8cc65e89569236f4f44/docs/using-wright.md) · [Implementation tests](https://github.com/burhop/wright/tree/85f97930927b672ddf7da8cc65e89569236f4f44/tests) · [October snapshot](wright-october-2026.md)
