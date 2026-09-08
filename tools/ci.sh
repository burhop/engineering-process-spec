#!/bin/sh
# Linux host: Docker and Node 24.13.1/npm. Build may access package registries.
set -eu
cd "$(dirname "$0")/.."
mkdir -p .work/ci-wheels
npm ci --prefix applications/node --ignore-scripts
npm test --prefix applications/node
docker build --tag eps-workflow-baseline:20260907 experiments/workflow-baseline
docker run --rm --mount "type=bind,source=$(pwd),target=/work" eps-workflow-baseline:20260907 python -m pip wheel --no-deps . --wheel-dir .work/ci-wheels
docker run --rm --network none --mount "type=bind,source=$(pwd),target=/work" eps-workflow-baseline:20260907 sh tools/ci-container.sh
npm pack ./applications/node --pack-destination .work/ci-wheels
python3 tools/adopter-walkthrough/run.py --wheel .work/ci-wheels/engineering_process_kit-0.1.0.dev1-py3-none-any.whl --node-package .work/ci-wheels/epx-node-adopter-0.1.0-draft.1.tgz --example examples/calculation --provider tests/providers/mock_mcp_server.py --out .work/ci-adopter
