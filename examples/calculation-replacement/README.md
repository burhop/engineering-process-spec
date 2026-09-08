# An explicit application-provider replacement

This is a deliberately authored revision **2** of the
[calculation](../calculation/README.md) process. It changes the required
application from `urn:engineering-process-spec:mock-engineering` to
`urn:engineering-process-spec:mock-other-engineering`. Both applications are
test fixtures; this is not a CAD-format converter or a Solid Edge substitute.

The prior [requirements](provenance/replaced-requirements.json) are retained as
labelled provenance. The new [requirements.json](requirements.json) and its
referenced CWL entrypoint are the only current authority. Input bytes, tool
snapshots and graph connections remain unchanged; their mappings must still
validate, and acceptance must use a new run's evidence. Old results or approval
subjects cannot silently carry over to the new revision.

Start from the [shared local setup](../README.md). Copy its receiving binding
file to `/tmp/epx-replacement-bindings.json`, then explicitly update
`bindings.engineering.application.id` and append the corresponding launcher
arguments:

```json
{
  "application.id": "urn:engineering-process-spec:mock-other-engineering",
  "appendToTransportArguments": ["--application", "urn:engineering-process-spec:mock-other-engineering"]
}
```

This snippet explains the two edits; it is not a replacement bindings-file
schema. Preserve the real file's existing implementation, version, transport and
launcher-trust fields. Then run:

```sh
epx validate examples/calculation-replacement
epx run examples/calculation-replacement --bindings /tmp/epx-replacement-bindings.json --engine cwltool --out /tmp/epx-replacement-python
node applications/node/cli.mjs run examples/calculation-replacement --bindings /tmp/epx-replacement-bindings.json --engine streamflow --out /tmp/epx-replacement-node
```

The new package with the **old** application binding must report unavailable
and make zero engineering calls. The original revision with the **new** binding
must also be unavailable. Only the explicitly matching new package and new
application may execute, producing the expected `0.157 kg` with new provenance.
This is different from changing an endpoint/path for the same intended provider,
which is receiving configuration and does not change the process revision.
