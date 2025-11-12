#!/bin/bash
# ===================================================================
# Script de Inicialização Git - Sistema Financeiro Pessoal
# ===================================================================
# Este script prepara o repositório Git e envia para GitHub
# ===================================================================

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}\n========================================"
echo -e "  Git Setup - Sistema Financeiro"
echo -e "========================================\n${NC}"

# Verificar se git está instalado
if ! command -v git &> /dev/null; then
    echo -e "${RED}[✗] Git não encontrado. Instale em: https://git-scm.com${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Git encontrado: $(git --version)${NC}"

# Verificar se já é um repositório git
if [ -d ".git" ]; then
    echo -e "\n${YELLOW}[!] Repositório Git já existe${NC}"
    read -p "Deseja continuar mesmo assim? (s/N): " response
    if [[ "$response" != "s" ]]; then
        echo -e "${YELLOW}[!] Operação cancelada${NC}"
        exit 0
    fi
else
    echo -e "\n${GREEN}[✓] Inicializando repositório Git...${NC}"
    git init
fi

# Adicionar todos os arquivos
echo -e "\n${GREEN}[✓] Adicionando arquivos ao Git...${NC}"
git add .

# Verificar o que será commitado
echo -e "\n${YELLOW}Arquivos para commit:${NC}"
git status --short

# Confirmar
read -p $'\nContinuar com o commit? (S/n): ' response
if [[ "$response" == "n" ]]; then
    echo -e "${YELLOW}[!] Operação cancelada${NC}"
    exit 0
fi

# Fazer commit
echo -e "\n${GREEN}[✓] Criando commit inicial...${NC}"
git commit -m "Initial commit - Sistema Financeiro Pessoal"

# Pedir URL do repositório GitHub
echo -e "\n${GREEN}========================================"
echo -e "  Configurar GitHub Remote"
echo -e "========================================\n${NC}"
echo -e "${YELLOW}Crie um repositório no GitHub:"
echo "  1. Acesse: https://github.com/new"
echo "  2. Nome: sistema-financeiro-pessoal"
echo "  3. NÃO adicione README, .gitignore ou license"
echo -e "  4. Clique em 'Create repository'\n${NC}"

read -p "Cole a URL do seu repositório GitHub (ex: https://github.com/usuario/repo.git): " githubUrl

if [ -z "$githubUrl" ]; then
    echo -e "\n${YELLOW}[!] URL não fornecida. Você pode adicionar depois:"
    echo "  git remote add origin <URL>"
    echo -e "  git push -u origin main\n${NC}"
    exit 0
fi

# Verificar se remote já existe
if git remote | grep -q "origin"; then
    echo -e "\n${YELLOW}[!] Remote 'origin' já existe. Removendo...${NC}"
    git remote remove origin
fi

# Adicionar remote
echo -e "\n${GREEN}[✓] Adicionando remote 'origin'...${NC}"
git remote add origin "$githubUrl"

# Renomear branch para main
echo -e "${GREEN}[✓] Configurando branch principal como 'main'...${NC}"
git branch -M main

# Push para GitHub
echo -e "\n${GREEN}[✓] Enviando para GitHub...${NC}"
if git push -u origin main; then
    echo -e "\n${GREEN}========================================"
    echo -e "  ✓ Sucesso!"
    echo -e "========================================\n${NC}"
    echo -e "${GREEN}Seu código está no GitHub!${NC}"
    echo -e "\n${YELLOW}Próximos passos:"
    echo "  1. Leia DEPLOY.md para instruções de deploy"
    echo "  2. Escolha uma plataforma (Railway, Render, Fly.io)"
    echo "  3. Configure as variáveis de ambiente"
    echo -e "  4. Faça o deploy!\n${NC}"
else
    echo -e "\n${RED}[✗] Erro no push para GitHub${NC}"
    echo -e "\nVerifique se:"
    echo "  - A URL está correta"
    echo "  - Você tem permissão no repositório"
    echo -e "  - Suas credenciais Git estão configuradas\n"
    exit 1
fi
