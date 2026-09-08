# Windows-only, optional rejection reproduction; does not access Wright.
$ErrorActionPreference = 'Stop'
$baselineDir = $PSScriptRoot
$baselineWork = Join-Path $baselineDir '.work'
New-Item -ItemType Directory -Force $baselineWork | Out-Null
$synapseRevision = 'ba3fbfd5125995bba9fb5900aed181a0775d538c'
$synapseArchive = Join-Path $baselineWork 'synapse.zip'
$synapseSource = Join-Path $baselineWork "synapse-$synapseRevision"
if (-not (Test-Path -LiteralPath $synapseSource)) {
    Invoke-WebRequest "https://codeload.github.com/serverlessworkflow/synapse/zip/$synapseRevision" -OutFile $synapseArchive
    Expand-Archive -LiteralPath $synapseArchive -DestinationPath $baselineWork
}
$jqPath = Join-Path $baselineWork 'jq.exe'
if (-not (Test-Path -LiteralPath $jqPath)) {
    Invoke-WebRequest 'https://github.com/jqlang/jq/releases/download/jq-1.8.1/jq-windows-amd64.exe' -OutFile $jqPath
}
Invoke-WebRequest 'https://raw.githubusercontent.com/jqlang/jq/jq-1.8.1/COPYING' -OutFile (Join-Path $baselineWork 'jq-COPYING')
if ((Get-FileHash -LiteralPath $jqPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne '23cb60a1354eed6bcc8d9b9735e8c7b388cd1fdcb75726b93bc299ef22dd9334') {
    throw 'jq checksum differs from the official 1.8.1 release checksum'
}
$env:DOTNET_CLI_HOME = $baselineWork
$env:NUGET_PACKAGES = Join-Path $baselineWork 'nuget'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:PATH = $baselineWork + [IO.Path]::PathSeparator + $env:PATH
dotnet build (Join-Path $synapseSource 'src/runner/Synapse.Runner/Synapse.Runner.csproj') --configuration Release --nologo
if ($LASTEXITCODE -ne 0) { throw 'Synapse build failed' }
$runner = Join-Path $synapseSource 'src/runner/Synapse.Runner/bin/Release/net9.0/Synapse.Runner.dll'
foreach ($probeArtifactName in @('synapse-control-result.json', 'synapse-control-jq.log', 'synapse-mcp-result.json', 'synapse-mcp.log')) {
    $probeArtifactPath = Join-Path $baselineWork $probeArtifactName
    if (Test-Path -LiteralPath $probeArtifactPath) { Remove-Item -LiteralPath $probeArtifactPath }
}
dotnet $runner --workflow (Join-Path $baselineDir 'ows-control.json') --output (Join-Path $baselineWork 'synapse-control-result.json') --logs (Join-Path $baselineWork 'synapse-control-jq.log')
$controlResult = Get-Content -Raw (Join-Path $baselineWork 'synapse-control-result.json') | ConvertFrom-Json
if ($controlResult.received.value -ne 2.5 -or $controlResult.received.unit -ne 'mm') { throw 'Synapse control did not produce the expected handoff' }
dotnet $runner --workflow (Join-Path $baselineDir 'ows-mcp.json') --output (Join-Path $baselineWork 'synapse-mcp-result.json') --logs (Join-Path $baselineWork 'synapse-mcp.log')
# This runner returns exit 0 even after task initialization failed.
$mcpLog = Get-Content -Raw (Join-Path $baselineWork 'synapse-mcp.log')
if (-not $mcpLog.Contains("Unknown/unsupported function 'mcp'")) { throw 'Observed behavior differs from the recorded MCP rejection; inspect logs' }
Write-Output 'Control handoff passed; native MCP call was rejected as unsupported.'
