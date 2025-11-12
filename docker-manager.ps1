# ==============================================================================
# Scripts Docker - Sistema Financeiro Pessoal
# ==============================================================================
# PowerShell script para gerenciar o sistema via Docker
# ==============================================================================

# Cores para output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

# Banner
function Show-Banner {
    Write-Host ""
    Write-Host "  💼 Sistema Financeiro Pessoal - Docker Manager" -ForegroundColor Cyan
    Write-Host "  ================================================" -ForegroundColor Cyan
    Write-Host ""
}

# Menu principal
function Show-Menu {
    Write-Host "  Escolha uma opção:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1] 🔨 Build - Construir imagem Docker"
    Write-Host "  [2] 🚀 Start - Iniciar aplicação"
    Write-Host "  [3] 🛑 Stop - Parar aplicação"
    Write-Host "  [4] 🔄 Restart - Reiniciar aplicação"
    Write-Host "  [5] 📊 Status - Ver status dos containers"
    Write-Host "  [6] 📝 Logs - Ver logs da aplicação"
    Write-Host "  [7] 🔍 Shell - Acessar shell do container"
    Write-Host "  [8] 🧹 Clean - Limpar containers e imagens"
    Write-Host "  [9] 🌐 Open - Abrir no navegador"
    Write-Host "  [0] ❌ Sair"
    Write-Host ""
}

# Verificar se Docker está instalado
function Test-Docker {
    try {
        docker --version | Out-Null
        return $true
    } catch {
        Write-Error "❌ Docker não está instalado ou não está no PATH!"
        Write-Info "Baixe em: https://www.docker.com/products/docker-desktop"
        return $false
    }
}

# Build da imagem
function Invoke-DockerBuild {
    Write-Info "🔨 Construindo imagem Docker..."
    docker-compose build
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Imagem construída com sucesso!"
    } else {
        Write-Error "❌ Erro ao construir imagem!"
    }
}

# Iniciar aplicação
function Start-App {
    Write-Info "🚀 Iniciando aplicação..."
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Aplicação iniciada!"
        Write-Info "📍 Acesse: http://localhost:8001"
        Start-Sleep -Seconds 2
        Invoke-AppStatus
    } else {
        Write-Error "❌ Erro ao iniciar aplicação!"
    }
}

# Parar aplicação
function Stop-App {
    Write-Info "🛑 Parando aplicação..."
    docker-compose down
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Aplicação parada!"
    } else {
        Write-Error "❌ Erro ao parar aplicação!"
    }
}

# Reiniciar aplicação
function Restart-App {
    Write-Info "🔄 Reiniciando aplicação..."
    docker-compose restart
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Aplicação reiniciada!"
    } else {
        Write-Error "❌ Erro ao reiniciar aplicação!"
    }
}

# Status dos containers
function Invoke-AppStatus {
    Write-Info "📊 Status dos containers:"
    Write-Host ""
    docker-compose ps
    Write-Host ""
    
    # Verificar se está rodando
    $status = docker-compose ps -q
    if ($status) {
        Write-Success "✅ Container está rodando!"
        
        # Testar conexão
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8001/api/diagnostico" -UseBasicParsing -TimeoutSec 3
            Write-Success "✅ API respondendo corretamente!"
        } catch {
            Write-Warning "⚠️  Container rodando mas API não responde ainda..."
        }
    } else {
        Write-Warning "⚠️  Container não está rodando!"
    }
}

# Ver logs
function Show-Logs {
    Write-Info "📝 Logs da aplicação (Ctrl+C para sair):"
    Write-Host ""
    docker-compose logs -f --tail=50
}

# Acessar shell
function Enter-Shell {
    Write-Info "🔍 Acessando shell do container..."
    docker-compose exec app /bin/bash
}

# Limpar tudo
function Clear-Docker {
    Write-Warning "🧹 Isso vai remover containers, imagens e volumes não utilizados!"
    $confirm = Read-Host "Confirma? (s/N)"
    
    if ($confirm -eq "s" -or $confirm -eq "S") {
        Write-Info "Parando containers..."
        docker-compose down -v
        
        Write-Info "Removendo imagens..."
        docker rmi sistema-financeiro:latest -f 2>$null
        
        Write-Info "Limpando sistema Docker..."
        docker system prune -f
        
        Write-Success "✅ Limpeza concluída!"
    } else {
        Write-Info "Operação cancelada."
    }
}

# Abrir no navegador
function Open-Browser {
    Write-Info "🌐 Abrindo navegador..."
    Start-Process "http://localhost:8001/dashboard"
}

# ==============================================================================
# MAIN
# ==============================================================================

Show-Banner

# Verificar Docker
if (-not (Test-Docker)) {
    exit 1
}

# Loop do menu
do {
    Show-Menu
    $option = Read-Host "Digite a opção"
    Write-Host ""
    
    switch ($option) {
        "1" { Invoke-DockerBuild }
        "2" { Start-App }
        "3" { Stop-App }
        "4" { Restart-App }
        "5" { Invoke-AppStatus }
        "6" { Show-Logs }
        "7" { Enter-Shell }
        "8" { Clear-Docker }
        "9" { Open-Browser }
        "0" { 
            Write-Success "👋 Até logo!"
            exit 0
        }
        default { Write-Warning "⚠️  Opção inválida!" }
    }
    
    Write-Host ""
    Write-Host "Pressione ENTER para continuar..."
    Read-Host
    Clear-Host
    Show-Banner
    
} while ($true)
