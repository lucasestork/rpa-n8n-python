param([string]$N8nCliScript = '',[string]$NodeExecutable = 'node')
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Prepare-N8n.ps1') -N8nCliScript $N8nCliScript
& $NodeExecutable $N8nCliScript 'import:workflow' --input (Join-Path $projectRoot 'workflows/briefing-rpa.json')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $NodeExecutable $N8nCliScript 'publish:workflow' --id RpaDioDemo2026
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'Demonstração local em http://127.0.0.1:5679. A base antiga não é usada. Ctrl+C encerra.'
& $NodeExecutable $N8nCliScript start
