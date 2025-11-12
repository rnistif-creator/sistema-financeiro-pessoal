# Script de monitoramento e auto-restart do servidor FastAPI
# Verifica a cada 20 segundos se o servidor está respondendo

param(
    [int]$Port,
    [int]$CheckInterval = 20,
    [int]$TimeoutSec = 10
)

# Porta escolhida: parâmetro > variável de ambiente PORT > 8001
if ($PSBoundParameters.ContainsKey('Port')) {
    $PORT = $Port
} elseif ($env:PORT) {
    try { $PORT = [int]$env:PORT } catch { $PORT = 8001 }
} else {
    $PORT = 8001
}
$VENV_PYTHON = "$PSScriptRoot\.venv\Scripts\python.exe"
$PROJECT_DIR = $PSScriptRoot
$CHECK_INTERVAL = $CheckInterval  # segundos
$TIMEOUT = $TimeoutSec  # segundos para timeout da requisição

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Monitor Auto-Restart - Sistema Financeiro" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Porta em uso: $PORT" -ForegroundColor Cyan

function Start-Server {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Iniciando servidor..." -ForegroundColor Yellow
    
    # Matar processos Python existentes na porta
    $existingProcess = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue
    if ($existingProcess) {
        $portPid = $existingProcess.OwningProcess
        Stop-Process -Id $portPid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # Mudar para o diretório do projeto e iniciar
    Push-Location $PROJECT_DIR
    
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $VENV_PYTHON
    $pinfo.Arguments = "-m uvicorn app.main:app --reload --port $PORT"
    $pinfo.WorkingDirectory = $PROJECT_DIR
    $pinfo.UseShellExecute = $false
    $pinfo.CreateNoWindow = $true
    
    $global:serverProcess = New-Object System.Diagnostics.Process
    $global:serverProcess.StartInfo = $pinfo
    [void]$global:serverProcess.Start()
    
    Pop-Location
    
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Servidor iniciado (PID: $($global:serverProcess.Id))" -ForegroundColor Green
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] URL: http://localhost:$PORT" -ForegroundColor Green
    Write-Host ""
    
    # Aguardar 5 segundos para o servidor inicializar
    Start-Sleep -Seconds 5
}

function Test-ServerHealth {
    # Verificação completa usando o script check_site.ps1
    # Confere /health, /api/health e páginas principais (dashboard, recorrentes, parcelas)
    $baseUrl = "http://localhost:$PORT"
    $checker = Join-Path $PSScriptRoot 'check_site.ps1'

    if (-not (Test-Path $checker)) {
        Write-Host "[!] check_site.ps1 não encontrado, caindo para verificação simples em /health" -ForegroundColor Yellow
        try {
            $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -TimeoutSec $TIMEOUT -ErrorAction Stop
            return $response.StatusCode -eq 200
        } catch { return $false }
    }

    try {
        & $checker -BaseUrl $baseUrl -TimeoutSec $TIMEOUT | Write-Host
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        Write-Host "[ERROR] Falha ao executar check_site.ps1: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Stop-Server {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Parando servidor..." -ForegroundColor Red
    
    if ($global:serverProcess -and !$global:serverProcess.HasExited) {
        Stop-Process -Id $global:serverProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    # Garantir que liberou a porta
    $connection = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue
    if ($connection) {
        Stop-Process -Id $connection.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    
    Start-Sleep -Seconds 2
}

# Iniciar servidor pela primeira vez
Start-Server

$consecutiveFailures = 0
$MAX_FAILURES = 2  # Reiniciar após 2 falhas consecutivas

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Monitoramento ativo - verificando a cada $CHECK_INTERVAL segundos" -ForegroundColor Cyan
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Pressione Ctrl+C para parar" -ForegroundColor Gray
Write-Host ""

try {
    while ($true) {
        Start-Sleep -Seconds $CHECK_INTERVAL
        
        $isHealthy = Test-ServerHealth
        
        if ($isHealthy) {
            if ($consecutiveFailures -gt 0) {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✓ Site recuperado!" -ForegroundColor Green
            } else {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✓ Site OK" -ForegroundColor DarkGreen
            }
            $consecutiveFailures = 0
        }
        else {
            $consecutiveFailures++
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✗ Falha na verificação completa ($consecutiveFailures/$MAX_FAILURES)" -ForegroundColor Yellow
            
            if ($consecutiveFailures -ge $MAX_FAILURES) {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ⚠ Servidor não responde! Reiniciando..." -ForegroundColor Red
                Write-Host ""
                
                Stop-Server
                Start-Server
                
                $consecutiveFailures = 0
            }
        }
    }
}
finally {
    Write-Host ""
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Encerrando monitor..." -ForegroundColor Yellow
    Stop-Server
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Monitor encerrado" -ForegroundColor Gray
}
