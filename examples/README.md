# Examples

These examples name the test provider
`urn:engineering-process-spec:mock-mcp` and application
`urn:engineering-process-spec:mock-engineering` explicitly. They do not represent
Solid Edge. Dimensions and density are synthetic test inputs, not design advice
or certified material properties.

| Example | Purpose | Expected outcome |
|---|---|---|
| [Minimal](minimal/README.md) | One named MCP call with complete dependencies, inputs and acceptance | Volume `0.00002 m3` |
| [Calculation](calculation/README.md) | Volume → mass using explicit CWL file handoff | Mass `0.157 kg` |
| [Mock handoff](mock-handoff/README.md) | Two reads followed by an explicit mock mutation | Recorded mass; failures retain upstream evidence |
| [Explicit replacement](calculation-replacement/README.md) | A deliberate application-provider edit with a new process revision | Requires the newly named application and renewed acceptance |
| [Inspection and approval](inspection-approval/README.md) | Required human-approval feature outside the core | Preserved and reported unsupported; zero engineering calls |
| [Solid Edge capture](solid-edge-capture/README.md) | Authentic historical identity and unavailable-provider transfer requirements | Capture-required, non-executable template; no invented live pins |

Each executable package contains one packed CWL authority, requirement manifest,
input job, captured mock tool contracts and RO-Crate 1.2 byte inventory.
`expected.json` states assertions to verify; it is **not an observed run report**.
Its quantity values must never replace actual tool results in acceptance checks.

The shared setup below assumes the CLI and both engines have been installed by
the repository quickstart, with `/repo` as this repository's Linux mount. It
creates receiving configuration outside every shared package:

```sh
epx demo-bindings --provider /repo/tests/providers/mock_mcp_server.py --out /tmp/epx-bindings.json
epx validate examples/calculation
epx inspect examples/calculation
epx preflight examples/calculation --bindings /tmp/epx-bindings.json
epx run examples/calculation --bindings /tmp/epx-bindings.json --engine cwltool --out /tmp/epx-calculation-python
node applications/node/cli.mjs run examples/calculation --bindings /tmp/epx-bindings.json --engine streamflow --out /tmp/epx-calculation-node
```

Use new output directories for each run. Adapt the repository/provider path to
your installation; do not edit process identity when changing that local path.
The profile-aware driver checks provider/resource identity, passes run context
to the selected adapter and consumes the required profile extension in a
temporary execution copy. The original CWL bytes remain authoritative.

To reproduce or check generated payloads after an intentional fixture update:

```sh
python tools/build_examples.py
python tools/build_examples.py --check
```

Generation pins the mock launcher's current bytes and copies the explicit tool
snapshots. A changed source launcher requires deliberate regeneration and renewed
test evidence. This is a development convenience, not permission to upgrade a
received process. Local credentials, endpoints and run-context files are never
generated inside the shared packages.

The source and specification explain the graphs without the generator: a new
application consumes the actual `workflow.cwl.json`, `requirements.json` and
referenced artifacts. It does not import this generator or any Wright module.
