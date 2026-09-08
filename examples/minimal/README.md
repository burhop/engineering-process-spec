# One fixed MCP call

The smallest complete core example calls the **named mock** operation
`engineering.volume` once. Length `100 mm`, width `80 mm` and thickness `2.5 mm`
produce `0.00002 m3`. Acceptance checks actual returned quantity meaning, unit
and value with absolute tolerance `0.000000000001 m3`.

Follow the [shared setup](../README.md), then run:

```sh
epx validate examples/minimal
epx run examples/minimal --bindings /tmp/epx-bindings.json --engine cwltool --out /tmp/epx-minimal-python
node applications/node/cli.mjs run examples/minimal --bindings /tmp/epx-bindings.json --engine streamflow --out /tmp/epx-minimal-node
```

The package still declares the mock resource `mock://plate`, revision `r1`.
The binder must verify it and the exact mock implementation/application before
the call. Missing provider configuration leaves the package intact and blocks
execution. Opening or inspecting the package makes no engineering calls.

Read [workflow.cwl.json](workflow.cwl.json) for the complete execution graph,
[inputs/job.json](inputs/job.json) for traceable synthetic inputs and
[requirements.json](requirements.json) for the identities/acceptance rule.
All required bytes are inventoried in [ro-crate-metadata.json](ro-crate-metadata.json).
The `epx_context` input is supplied by the receiving driver, not by the author.
