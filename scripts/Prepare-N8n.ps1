param([string]$N8nCliScript = '')
$projectRoot = Split-Path $PSScriptRoot -Parent
if (-not $N8nCliScript) {
  $cacheRoot = Join-Path $env:LOCALAPPDATA 'npm-cache/_npx'
  foreach ($candidate in (Get-ChildItem -LiteralPath $cacheRoot -Directory -ErrorAction SilentlyContinue)) {
    $manifestPath = Join-Path $candidate.FullName 'node_modules/n8n/package.json'
    if (Test-Path -LiteralPath $manifestPath) {
      $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
      if ($manifest.version -eq '2.22.6') { $N8nCliScript = Join-Path $candidate.FullName 'node_modules/n8n/bin/n8n'; break }
    }
  }
}
if (-not $N8nCliScript -or -not (Test-Path -LiteralPath $N8nCliScript)) {
  throw 'Informe -N8nCliScript com o arquivo bin/n8n da sua instalação. O projeto foi testado com n8n 2.22.6.'
}
$env:N8N_USER_FOLDER = Join-Path $projectRoot '.runtime/n8n'
$env:N8N_DIAGNOSTICS_ENABLED = 'false'
$env:N8N_PORT = '5679'
$env:N8N_LISTEN_ADDRESS = '127.0.0.1'
$env:N8N_RUNNERS_BROKER_PORT = '5689'
New-Item -ItemType Directory -Path $env:N8N_USER_FOLDER -Force | Out-Null
