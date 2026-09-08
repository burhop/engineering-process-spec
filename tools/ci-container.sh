#!/bin/sh
# Reuses the locked Linux engine environment. Core execution has no network.
set -eu
cd /work
python -m pip install --no-index --no-deps --force-reinstall .work/ci-wheels/engineering_process_kit-0.1.0.dev1-py3-none-any.whl
python tests/providers/test_mock_mcp.py --report .work/ci-provider-results.json
python tools/check.py --out .work/ci-repository-checks.json
python tests/conformance/run_core.py --out .work/ci-conformance
python tools/check.py --report .work/ci-conformance/report.json --out .work/ci-repository-checks-final.json
