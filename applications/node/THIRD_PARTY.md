# JavaScript dependency attribution

This application uses dependencies through their published package interfaces.
It does not copy Wright source or Python adapter/resolver logic. Installation
retains the upstream packages' LICENSE files. The lockfile identifies exact
direct/transitive package versions, registry locations and integrity hashes.

| Direct dependency | Revision | Upstream license / source |
|---|---|---|
| Ajv | 8.18.0 | MIT; [official repository](https://github.com/ajv-validator/ajv), installed `node_modules/ajv/LICENSE` |
| yauzl | 3.2.1 | MIT; [official repository](https://github.com/thejoshwolfe/yauzl), installed `node_modules/yauzl/LICENSE` |

The installed transitive packages also retain their respective notices; consult
`package-lock.json` and their LICENSE files before packaging a distribution.
Preserving dependency notices does not select licensing or contributor-IP terms
for this repository's own specification or implementation.
