# Author a process people and applications can exchange

Start with [minimal](../examples/minimal/README.md) or
[calculation](../examples/calculation/README.md). Read the
[core requirements](../spec/core-draft.md) for normative meaning. The authoring
format is ordinary packed **CWL v1.2 JSON**, with a required exchange profile and
RO-Crate 1.2 files. There is no separate task grammar to learn or hidden Wright
base to reconstruct.

## Know which file supplies which fact

| File | Authoritative content |
|---|---|
| `workflow.cwl.json` | The `#main` graph, inputs, steps, expressions, outputs and adapter invocation |
| `requirements.json` | Process/profile revisions, intended provider/application identities, operations, resources and acceptance |
| `contracts/*.tool.json` | Captured named tool descriptor, including exact input/output schemas |
| `inputs/job.json` | Explicit default input values and units; no receiving context or secrets |
| `ro-crate-metadata.json` | Entrypoint/profile relationships and SHA-256 inventory of required bytes |
| `expected.json` in examples | Informative expected observations; never replacement measurement evidence |

Local endpoint, credentials, launch command and machine paths belong in receiving
bindings, outside the package. Keep a supplied original Wright source as labelled
provenance and record translation gaps; a new application must not consult it as
a second independently editable authority.

The RO-Crate root also records its name, description, availability date and
license information. These local examples use the draft's availability date and
state explicitly that licensing terms have not been selected. That metadata is
neither a public-release claim nor a grant of additional permissions.

## Annotated real example

These are excerpts from the complete
[minimal CWL file](../examples/minimal/workflow.cwl.json), not standalone files.
The graph declares its indispensable exchange requirement under `requirements`:

```json
"$namespaces": {"epx":"urn:engineering-process-spec:profile:"},
"requirements": {
  "epx:ExchangeRequirement":{"manifest":"requirements.json"},
  "InlineJavascriptRequirement":{},
  "StepInputExpressionRequirement":{},
  "MultipleInputFeatureRequirement":{}
}
```

Do not move the exchange requirement or named-provider obligations into `hints`.
An ordinary CWL engine must not silently execute without them. A profile-aware
driver first implements the requirement and then removes only that consumed
extension from a separately identified execution copy.

The volume step fixes its identity and passes the input quantities with a normal
CWL expression:

```json
"volume": {
  "run":"#mcp-call",
  "in":{
    "context":"epx_context",
    "node":{"default":"main/volume"},
    "binding":{"default":"engineering"},
    "tool":{"default":"engineering.volume"},
    "arguments_json":{
      "source":["length","width","thickness"],
      "valueFrom":"$(JSON.stringify({length:self[0],width:self[1],thickness:self[2]}))",
      "linkMerge":"merge_nested"
    }
  },
  "out":["result"]
}
```

The matching `operations["main/volume"]` in requirements fixes binding
`engineering`, tool `engineering.volume`, effect `read-only` and
`contracts/engineering.volume.tool.json`. The adapter must reject conflicting
node/binding/tool arguments before invocation. The `#mcp-call` CommandLineTool
declares `epx-mcp-call` and outputs `result.json` with `loadContents: true`.

The calculation's next step reads the actual preceding MCP result with
`JSON.parse(self[0].contents).structuredContent`. CWL supplies this edge; a host
or AI must not invent a different handoff. Acceptance references
`/structuredContent/value`, `/structuredContent/unit` and
`/structuredContent/quantity` on an observed successful result.

## Validation and correction loop

1. Copy the whole supported example into a new directory. Give intentional
   semantic edits a new process revision. Preserve the original and provenance.
2. Capture or obtain the exact intended implementation/application, versioned
   tool contract and identified input resources. If a fact is missing, record
   the gap and stop executable authoring at that point. Do not fill a live CAD
   pin from a display name, local UUID, tool-name similarity or guessed schema.
3. Edit graph inputs, fixed operation mappings and data edges using supported
   CWL constructs. Declare read-only versus mutation effects. Add measurable
   quantity criteria with units and tolerances or inclusive bounds.
4. Recompute the inventory for deliberately changed bytes. Then run
   `epx validate YOUR_PACKAGE` and review each diagnostic against its referenced
   requirement. Correct the authoring error; do not weaken a requirement or
   discard unknown content simply to get a pass.
5. Inspect the resulting graph/dependencies, preserve a no-op copy, and compare
   its bytes. Configure the receiving environment separately and preflight it.
   Unavailable execution is not an instruction to rewrite the process.
6. Run both advertised execution paths against the mock or an authorized isolated
   provider environment. Inspect actual calls, handoff, partial results and
   acceptance. Add or update a conformance case for each newly claimed behavior.

The repository's `python tools/build_examples.py --check` checks its generated
fixtures, not arbitrary user edits. Running the generator rewrites those example
fixtures; it is not a universal authoring command or conversion tool.

## Instructions for AI authors

Use the same files, captured facts and validator as a human author. Keep explicit
provider choices and unresolved facts in the output. Ask for the missing identity,
resource or contract rather than inventing it. A valid JSON shape is only the
first check: compare operation mappings, dimensions, resource revisions and
failure behavior, then use actual run evidence for acceptance.

An AI-directed Wright task is not automatically equivalent to a fixed call
sequence. Label a deterministic variant as newly authored unless equivalence is
demonstrated. Preserve unsupported approval/agent behavior and make its required
feature explicit; an AI verdict does not grant human approval.

Replacing a provider is an intentional edit, as shown by
[calculation-replacement](../examples/calculation-replacement/README.md): new
revision, named replacement, retained provenance and renewed validation/evidence.
Setting a different local endpoint for the same verified intended provider is
receiving configuration. Neither operation permits silent CAD substitution.
