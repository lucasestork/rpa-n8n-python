param([string]$N8nCliScript = '',[string]$NodeExecutable = 'node')
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Prepare-N8n.ps1') -N8nCliScript $N8nCliScript
# A API Python deve estar iniciada separadamente na porta 8765.
& $NodeExecutable $N8nCliScript 'import:workflow' --input (Join-Path $projectRoot 'workflows/briefing-rpa.json')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $NodeExecutable $N8nCliScript execute --id RpaDioDemo2026 --rawOutput
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
