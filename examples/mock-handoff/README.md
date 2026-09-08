# Handoff, explicit mutation and partial failure

This clearly named **mock** process runs volume → mass → record. The first two
operations are read-only calculations; `engineering.record` deliberately changes
the mock session's measurement store and resource revision from `r1` to `r2`.
It does not modify a CAD document or manufacture a part.

Follow the [shared setup](../README.md), then run:

```sh
epx run examples/mock-handoff --bindings /tmp/epx-bindings.json --engine cwltool --out /tmp/epx-handoff-python
node applications/node/cli.mjs run examples/mock-handoff --bindings /tmp/epx-bindings.json --engine streamflow --out /tmp/epx-handoff-node
```

Expected actual mass and stored measurement are `0.157 kg`; the record result
identifies the same mock application and `mock://plate`, revision `r2`.
Acceptance checks both upstream measurements and the recorded measurement.
The mock's stored state is session-scoped; its resource revision is not a
persistent engineering database commitment.

For a deterministic failure, copy the **receiving bindings file** to a new local
file and append these two arguments to its engineering stdio transport's
`arguments` array:

```json
["--fault", "tool-error", "--fault-tool", "engineering.record"]
```

Preserve its existing launcher arguments and identity/trust fields. Run the same
unchanged package with that local bindings file and a new output directory.
Expected execution is `failed`; volume and mass evidence remain available,
the record criterion is `not-run`, and a valid prior result is never invented
for the failed record node. The overall run is not accepted.

Use `disconnect-after-mutation` instead of `tool-error` to test a lost response
after the record may have changed state. Expected execution is `unknown`, with
no automatic retry or claimed rollback. Use `malformed-output`, `rpc-error`,
`wrong-unit` or `wrong-value` to distinguish other failure channels. These modes
belong solely to the test provider and never authorize fault injection against
an actual CAD service. The conformance report records which paths actually ran.
