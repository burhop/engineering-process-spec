$ErrorActionPreference = 'Stop'
$baselineDir = $PSScriptRoot
New-Item -ItemType Directory -Force (Join-Path $baselineDir '.work') | Out-Null
docker build --tag eps-workflow-baseline:20260907 $baselineDir
if ($LASTEXITCODE -ne 0) { throw 'Baseline image build failed' }
docker run --rm --network none --name eps-workflow-baseline-probe --mount "type=bind,source=$baselineDir,target=/work" eps-workflow-baseline:20260907 sh run-cwl.sh
if ($LASTEXITCODE -ne 0) { throw 'Baseline workflow verification failed' }
