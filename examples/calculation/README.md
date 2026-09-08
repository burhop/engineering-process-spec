# A calculation with explicit units and data handoff

This process first calls the named mock `engineering.volume`, then passes that
call's actual `structuredContent` to the same intended provider's
`engineering.mass` operation. Inputs are `100 × 80 × 2.5 mm` and test density
`7850 kg/m3`. Expected volume is `0.00002 m3`, expected mass is `0.157 kg`.
The density is a synthetic fixture input; this example certifies no material.

Follow the [shared setup](../README.md), then run:

```sh
epx validate examples/calculation
epx run examples/calculation --bindings /tmp/epx-bindings.json --engine cwltool --out /tmp/epx-calculation-python
node applications/node/cli.mjs run examples/calculation --bindings /tmp/epx-bindings.json --engine streamflow --out /tmp/epx-calculation-node
```

[workflow.cwl.json](workflow.cwl.json) uses ordinary CWL `source`, `valueFrom`
and `loadContents`. No host callback computes the edge: the volume result File
and density input feed the mass arguments expression. Every step declares fixed
node, binding and tool defaults that must match [requirements.json](requirements.json).
Its acceptance pointers target the original MCP result, not engine status text.

Expected execution is `succeeded`, acceptance is `pass`, and approval is
`not-requested`. The mass tolerance is `0.000001 kg`. The report must still tie
each measurement to its node, exact package/input bytes, intended and observed
provider/resource identity and actual result digest.

Changing a local launch path to another verified instance of this same mock is
receiving configuration. Selecting a different implementation or application
is an explicit process replacement requiring a new revision, updated operation
contracts and renewed validation. Equal arithmetic or equal tool names do not
authorize substitution.
