# Upstream material and unresolved project terms

This repository has not selected licenses for its own specification, code,
examples or contributor-IP policy. Dependency attribution is not a grant of
rights over the repository or permission to publish third-party CAD models.

The prototype uses upstream packages through their installed interfaces. Their
license files and package metadata remain with the installations; the repository
does not relabel these packages as its own source.

| Material | Exact reference and notice location |
|---|---|
| cwltool and StreamFlow engines | `3.2.20260720092025` and `0.2.0rc2`; [baseline sources and notices](experiments/workflow-baseline/README.md#upstream-sources-and-notices); installed distribution notices retained |
| Python engine dependencies | [Complete version lock](experiments/workflow-baseline/requirements.lock.txt); each installed package retains its own metadata/notices |
| Node receiver dependencies | [JavaScript attribution](applications/node/THIRD_PARTY.md) and exact integrity-pinned npm lock; installed LICENSE files retained |
| Python build/runtime packages | [setuptools 80.10.2](https://pypi.org/project/setuptools/80.10.2/), [wheel 0.46.3](https://pypi.org/project/wheel/0.46.3/), [jsonschema 4.26.0](https://pypi.org/project/jsonschema/4.26.0/); installed distribution notices retained |
| Node/Python container distributions | Base-image digests and retained notices in [Dockerfile](experiments/workflow-baseline/Dockerfile) |
| OWS/Synapse experimental material | [Probe source references and notice handling](experiments/workflow-baseline/README.md); downloaded source retains upstream notices; no modified Synapse runtime is distributed here |
| Referenced specifications | [Source register](research/sources.md); links and original analysis, not copied proprietary standards |
| Wright/Solid Edge observations | [Read-only source identities](research/wright.md); capture inputs stay local; redistribution rights and authentic fixture availability remain unresolved |
| CI actions | [checkout v4.2.2](https://github.com/actions/checkout/commit/11bd71901bbe5b1630ceea73d27597364c9af683) and [setup-node v4.4.0](https://github.com/actions/setup-node/commit/49933ea5288caeca8642d1e84afbd3f7d6820020), referenced by exact revision rather than vendored |

Generated mock examples describe this repository's synthetic fixture. They are
not copied vendor process definitions or evidence of Solid Edge behavior.
Before any distribution, review actual packaged material, notices, fixture
permissions and the owner's chosen terms. The [readiness decision](decisions/004-adoption-readiness.md)
keeps those choices separate from technical conformance.
