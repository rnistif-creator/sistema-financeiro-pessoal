# ===================================================================
# Script de Inicialização Git - Sistema Financeiro Pessoal
# ===================================================================
# Este script prepara o repositório Git e envia para GitHub
# ===================================================================

# Cores para output
$GREEN = "Green"
$YELLOW = "Yellow"
$RED = "Red"

Write-Host "`n========================================" -ForegroundColor $GREEN
Write-Host "  Git Setup - Sistema Financeiro" -ForegroundColor $GREEN
Write-Host "========================================`n" -ForegroundColor $GREEN

# Verificar se git está instalado
try {
    $gitVersion = git --version
    Write-Host "[✓] Git encontrado: $gitVersion" -ForegroundColor $GREEN
} catch {
    Write-Host "[✗] Git não encontrado. Instale em: https://git-scm.com" -ForegroundColor $RED
    exit 1
}

# Verificar se já é um repositório git
if (Test-Path ".git") {
    Write-Host "`n[!] Repositório Git já existe" -ForegroundColor $YELLOW
    $response = Read-Host "Deseja continuar mesmo assim? (s/N)"
    if ($response -ne "s") {
        Write-Host "[!] Operação cancelada" -ForegroundColor $YELLOW
        exit 0
    }
} else {
    Write-Host "`n[✓] Inicializando repositório Git..." -ForegroundColor $GREEN
    git init
}

# Adicionar todos os arquivos
Write-Host "`n[✓] Adicionando arquivos ao Git..." -ForegroundColor $GREEN
git add .

# Verificar o que será commitado
Write-Host "`nArquivos para commit:" -ForegroundColor $YELLOW
git status --short

# Confirmar
$response = Read-Host "`nContinuar com o commit? (S/n)"
if ($response -eq "n") {
    Write-Host "[!] Operação cancelada" -ForegroundColor $YELLOW
    exit 0
}

# Fazer commit
Write-Host "`n[✓] Criando commit inicial..." -ForegroundColor $GREEN
git commit -m "Initial commit - Sistema Financeiro Pessoal"

# Pedir URL do repositório GitHub
Write-Host "`n========================================" -ForegroundColor $GREEN
Write-Host "  Configurar GitHub Remote" -ForegroundColor $GREEN
Write-Host "========================================`n" -ForegroundColor $GREEN
Write-Host "Crie um repositório no GitHub:" -ForegroundColor $YELLOW
Write-Host "  1. Acesse: https://github.com/new"
Write-Host "  2. Nome: sistema-financeiro-pessoal"
Write-Host "  3. NÃO adicione README, .gitignore ou license"
Write-Host "  4. Clique em 'Create repository'`n"

$githubUrl = Read-Host "Cole a URL do seu repositório GitHub (ex: https://github.com/usuario/repo.git)"

if ([string]::IsNullOrWhiteSpace($githubUrl)) {
    Write-Host "`n[!] URL não fornecida. Você pode adicionar depois:" -ForegroundColor $YELLOW
    Write-Host "  git remote add origin <URL>"
    Write-Host "  git push -u origin main`n"
    exit 0
}

# Verificar se remote já existe
$remoteExists = git remote | Where-Object { $_ -eq "origin" }
if ($remoteExists) {
    Write-Host "`n[!] Remote 'origin' já existe. Removendo..." -ForegroundColor $YELLOW
    git remote remove origin
}

# Adicionar remote
Write-Host "`n[✓] Adicionando remote 'origin'..." -ForegroundColor $GREEN
git remote add origin $githubUrl

# Renomear branch para main
Write-Host "[✓] Configurando branch principal como 'main'..." -ForegroundColor $GREEN
git branch -M main

# Push para GitHub
Write-Host "`n[✓] Enviando para GitHub..." -ForegroundColor $GREEN
$pushResult = git push -u origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor $GREEN
    Write-Host "  ✓ Sucesso!" -ForegroundColor $GREEN
    Write-Host "========================================`n" -ForegroundColor $GREEN
    Write-Host "Seu código está no GitHub!" -ForegroundColor $GREEN
    Write-Host "`nPróximos passos:" -ForegroundColor $YELLOW
    Write-Host "  1. Leia DEPLOY.md para instruções de deploy"
    Write-Host "  2. Escolha uma plataforma (Railway, Render, Fly.io)"
    Write-Host "  3. Configure as variáveis de ambiente"
    Write-Host "  4. Faça o deploy!`n"
} else {
    Write-Host "`n[✗] Erro no push para GitHub:" -ForegroundColor $RED
    Write-Host $pushResult
    Write-Host "`nVerifique se:"
    Write-Host "  - A URL está correta"
    Write-Host "  - Você tem permissão no repositório"
    Write-Host "  - Suas credenciais Git estão configuradas`n"
    exit 1
}
