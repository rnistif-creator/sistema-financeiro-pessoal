#!/bin/bash

# ==============================================================================
# Scripts Docker - Sistema Financeiro Pessoal (Linux/Mac)
# ==============================================================================

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções auxiliares
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Banner
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "  💼 Sistema Financeiro Pessoal - Docker Manager"
    echo "  ================================================"
    echo -e "${NC}"
}

# Menu
show_menu() {
    echo -e "${YELLOW}Escolha uma opção:${NC}"
    echo ""
    echo "  [1] 🔨 Build - Construir imagem Docker"
    echo "  [2] 🚀 Start - Iniciar aplicação"
    echo "  [3] 🛑 Stop - Parar aplicação"
    echo "  [4] 🔄 Restart - Reiniciar aplicação"
    echo "  [5] 📊 Status - Ver status dos containers"
    echo "  [6] 📝 Logs - Ver logs da aplicação"
    echo "  [7] 🔍 Shell - Acessar shell do container"
    echo "  [8] 🧹 Clean - Limpar containers e imagens"
    echo "  [9] 🌐 Open - Abrir no navegador"
    echo "  [0] ❌ Sair"
    echo ""
}

# Verificar Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado!"
        echo "Instale em: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose não está instalado!"
        echo "Instale em: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Build
docker_build() {
    print_info "Construindo imagem Docker..."
    docker-compose build
    if [ $? -eq 0 ]; then
        print_success "Imagem construída com sucesso!"
    else
        print_error "Erro ao construir imagem!"
    fi
}

# Start
docker_start() {
    print_info "Iniciando aplicação..."
    docker-compose up -d
    if [ $? -eq 0 ]; then
        print_success "Aplicação iniciada!"
        print_info "Acesse: http://localhost:8001"
        sleep 2
        docker_status
    else
        print_error "Erro ao iniciar aplicação!"
    fi
}

# Stop
docker_stop() {
    print_info "Parando aplicação..."
    docker-compose down
    if [ $? -eq 0 ]; then
        print_success "Aplicação parada!"
    else
        print_error "Erro ao parar aplicação!"
    fi
}

# Restart
docker_restart() {
    print_info "Reiniciando aplicação..."
    docker-compose restart
    if [ $? -eq 0 ]; then
        print_success "Aplicação reiniciada!"
    else
        print_error "Erro ao reiniciar aplicação!"
    fi
}

# Status
docker_status() {
    print_info "Status dos containers:"
    echo ""
    docker-compose ps
    echo ""
    
    if docker-compose ps -q | grep -q .; then
        print_success "Container está rodando!"
        
        # Testar API
        if curl -s -f http://localhost:8001/api/diagnostico > /dev/null 2>&1; then
            print_success "API respondendo corretamente!"
        else
            print_warning "Container rodando mas API não responde ainda..."
        fi
    else
        print_warning "Container não está rodando!"
    fi
}

# Logs
docker_logs() {
    print_info "Logs da aplicação (Ctrl+C para sair):"
    echo ""
    docker-compose logs -f --tail=50
}

# Shell
docker_shell() {
    print_info "Acessando shell do container..."
    docker-compose exec app /bin/bash
}

# Clean
docker_clean() {
    print_warning "Isso vai remover containers, imagens e volumes não utilizados!"
    read -p "Confirma? (s/N): " confirm
    
    if [ "$confirm" = "s" ] || [ "$confirm" = "S" ]; then
        print_info "Parando containers..."
        docker-compose down -v
        
        print_info "Removendo imagens..."
        docker rmi sistema-financeiro:latest -f 2>/dev/null
        
        print_info "Limpando sistema Docker..."
        docker system prune -f
        
        print_success "Limpeza concluída!"
    else
        print_info "Operação cancelada."
    fi
}

# Open browser
open_browser() {
    print_info "Abrindo navegador..."
    
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8001/dashboard
    elif command -v open &> /dev/null; then
        open http://localhost:8001/dashboard
    else
        print_info "Acesse manualmente: http://localhost:8001/dashboard"
    fi
}

# ==============================================================================
# MAIN
# ==============================================================================

show_banner
check_docker

while true; do
    show_menu
    read -p "Digite a opção: " option
    echo ""
    
    case $option in
        1) docker_build ;;
        2) docker_start ;;
        3) docker_stop ;;
        4) docker_restart ;;
        5) docker_status ;;
        6) docker_logs ;;
        7) docker_shell ;;
        8) docker_clean ;;
        9) open_browser ;;
        0) 
            print_success "Até logo!"
            exit 0
            ;;
        *) print_warning "Opção inválida!" ;;
    esac
    
    echo ""
    read -p "Pressione ENTER para continuar..."
    show_banner
done
