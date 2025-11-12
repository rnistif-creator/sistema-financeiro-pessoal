#!/usr/bin/env python3
"""
Script de pré-inicialização para Render
Garante que diretórios necessários existem antes de iniciar o servidor
"""
import os
import sys
from pathlib import Path

def setup_directories():
    """Cria diretórios necessários se não existirem"""
    # Obter DB_PATH da variável de ambiente
    db_path = os.getenv("DB_PATH", "lancamentos.db")
    db_path_obj = Path(db_path)
    
    # Determinar diretório do banco de dados
    if db_path_obj.is_absolute():
        db_dir = db_path_obj.parent
    else:
        # Se for relativo, usar diretório atual
        db_dir = Path.cwd()
        # Garantir que o caminho completo existe
        full_path = db_dir / db_path_obj
        db_dir = full_path.parent
    
    # Criar diretório de dados se não existir
    try:
        db_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Diretório do banco criado: {db_dir}")
        
        # Verificar se conseguimos criar arquivos no diretório
        test_file = db_dir / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        print(f"✓ Permissões de escrita OK em {db_dir}")
    except Exception as e:
        print(f"✗ Erro ao criar/acessar diretório {db_dir}: {e}", file=sys.stderr)
        print(f"✗ Tentando criar diretórios intermediários...", file=sys.stderr)
        try:
            # Tentar criar todos os diretórios pais
            os.makedirs(db_dir, exist_ok=True)
            print(f"✓ Diretório criado com makedirs: {db_dir}")
        except Exception as e2:
            print(f"✗ Falha final ao criar diretório: {e2}", file=sys.stderr)
            sys.exit(1)
    
    # Criar diretório de backups
    backup_dir = Path.cwd() / "backups"
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Diretório de backups garantido: {backup_dir}")
    except Exception as e:
        print(f"✗ Erro ao criar diretório de backups: {e}", file=sys.stderr)
        # Não fatal - continuar mesmo se backups falhar
        pass
    
    print("✓ Configuração de diretórios concluída\n")

def check_database_url():
    """Verifica configuração do DATABASE_URL"""
    db_path = os.getenv("DB_PATH")
    database_url = os.getenv("DATABASE_URL")
    
    if database_url and not database_url.startswith("sqlite:"):
        print(f"✓ Usando DATABASE_URL externo (PostgreSQL/outro)")
    else:
        print(f"✓ Usando SQLite: {db_path or 'lancamentos.db'}")

if __name__ == "__main__":
    print("=" * 60)
    print("Pré-inicialização - Sistema Financeiro Pessoal")
    print("=" * 60)
    
    # Setup de diretórios
    setup_directories()
    
    # Verificar configuração de DB
    check_database_url()
    
    print("=" * 60)
    print("✓ Pronto para iniciar o servidor\n")
