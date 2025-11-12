param(
  [string]$BaseUrl = "http://localhost:8001",
  [int]$TimeoutSec = 10
)

# Simple automatic page and API health check for the Financeiro app
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Verificação automática do site ($BaseUrl)" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

$ErrorActionPreference = 'Stop'
$overallOk = $true

function Test-Endpoint {
  param(
    [string]$Path,
    [string]$Contains = $null,
    [string]$ExpectJsonKey = $null
  )
  $url = ("{0}{1}" -f $BaseUrl, $Path)
  try {
    $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec $TimeoutSec -UseBasicParsing
    $ok = $response.StatusCode -eq 200

    if ($ok -and $ExpectJsonKey) {
      try {
        $json = $response.Content | ConvertFrom-Json
        if (-not ($json.PSObject.Properties.Name -contains $ExpectJsonKey)) { $ok = $false }
      } catch { $ok = $false }
    }

    if ($ok -and $Contains) {
      if ($response.Content -notmatch [Regex]::Escape($Contains)) { $ok = $false }
    }

    if ($ok) {
      Write-Host ("[OK] {0}" -f $Path) -ForegroundColor Green
      return $true
    } else {
      Write-Host ("[FAIL] {0}" -f $Path) -ForegroundColor Red
      return $false
    }
  } catch {
    Write-Host ("[ERROR] {0} -> {1}" -f $Path, $_.Exception.Message) -ForegroundColor Red
    return $false
  }
}

# API health checks
$overallOk = (Test-Endpoint -Path "/health" -ExpectJsonKey "status") -and $overallOk
$overallOk = (Test-Endpoint -Path "/api/health" -ExpectJsonKey "status") -and $overallOk

# Key pages checks
$overallOk = (Test-Endpoint -Path "/dashboard" -Contains "Dashboard - Sistema Financeiro") -and $overallOk
$overallOk = (Test-Endpoint -Path "/recorrentes" -Contains "Lançamentos Recorrentes") -and $overallOk
$overallOk = (Test-Endpoint -Path "/parcelas" -Contains "Parcelas") -and $overallOk

Write-Host "" 
if ($overallOk) {
  Write-Host "✔ Todas as verificações passaram" -ForegroundColor Green
  exit 0
} else {
  Write-Host "✖ Uma ou mais verificações falharam" -ForegroundColor Red
  exit 1
}