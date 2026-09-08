# Experimental conformance evidence

This finite suite tests the [core draft](../spec/core-draft.md), with requirement
IDs and [use-case](../use-cases/interoperability.md) IDs mapped in
[cases.json](cases.json). A schema pass, engine exit code, or successful MCP call
alone does not establish conformance. The harness invokes public applications;
it never imports either implementation's resolver or adapter.

Install the Python distribution, the independent Node application and their
pinned workflow engines using the [adopter instructions](../docs/quickstart.md).
Then run from the repository root in that environment:

```text
python tests/conformance/run_core.py --out .work/conformance-run
```

The output directory must be new or empty. Set `EPX_NODE_CLI` to the installed
Node application's `cli.mjs` to test that distribution; otherwise the checked-in
Node application is used. `EPX_PYTHON` is set for the child engine/adapter launch.
`--implementation python|node|both`, repeated `--case ID`, and `--list` support
diagnosis. `--jobs 4` runs independent cases concurrently; each case keeps its
own provider state, inputs and output directory. A partial selection never
produces a full-core claim. `EPX_NODE_ARCHIVE` optionally identifies an installed
tarball: every archived file is compared with the actual application bytes.
`EPX_CONTAINER_IMAGE_ID` records a verified container image digest when used.

The [runner](../tests/conformance/run_core.py) produces `report.json`, per-case
assertions, exact CLI arguments/stdout/stderr, separate provider audits, copies
of deliberately edited fixtures and their inventories, and run reports/raw
artifacts. Every case gets a separate run and audit path. Recorded hashes identify
the actual installed Python files and wheel origin, Node files, specification,
schemas, test code and fixture bytes; sources changing during a run prevent a
full-core claim. Retain these identities with any reported result.

`passed` means the named assertions matched observed behavior. `failed` includes
an implementation mismatch or harness/setup error and must be investigated.
`unsupported` is a reported capability outcome, never a successful mandatory
case. `not run` means no execution evidence exists. Negative cases pass only
when the required rejection, preservation, diagnostic and no-call assertions
succeed. Requirement coverage means the mapped observable assertions passed;
it does not prove every possible behavior of an upstream standard.

Current roles are reader, binder, executor, adapter and an editor limited to
preservation and explicit provider replacement. Both execution paths use real
CWL engines and actual MCP messages with an explicitly named mock provider.
They share schemas, fixtures and some upstream parsing libraries; their
process readers, resolvers, adapters and implementation languages are distinct.
The HTTP case uses real loopback networking and controlled mock platform
metadata. It does not prove execution on another operating system or an
authenticated remote CAD service.

B06-UNKNOWN uses an [explicit test provider variant](../tests/conformance/resource_revision_shim.py)
that verifies the frozen mock's source digest, retains its actual MCP handlers
and audit, and omits the observed revision from a resource read. Its different
mock implementation identity and launcher digest are authored into a distinct
fixture revision and receiving binding. This exercises unverifiable resource
identity without changing the standard mock or silently replacing a provider.

Original real-CAD cases E02, E04 and E05, and richer approval case A03, remain
explicitly `not run`. Their mock counterparts use C-MCP IDs. These results
cannot establish Solid Edge interoperability, provider equivalence, product
certification or stable/public-release readiness. See the
[goal audit](../docs/goal-audit.md) and [maintenance gates](../docs/maintenance.md).

Retained reports belong under `conformance/results/`; temporary evidence belongs
under `.work/`. Do not replace failed reports with a passing summary without
retaining the tested artifact identities and explaining the corrected defect.
To retain a completed run compactly, use:

```text
python tests/conformance/export_evidence.py .work/conformance-run --out conformance/results/NEW-ID
```

This stores the top-level report and an evidence ZIP with every other original
file plus a digest manifest. Extract the archive beside the report to resolve
its per-case evidence paths. The report records the original report digest and
archive digest; export does not convert failed or partial results into success.
