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
    
    # Se for caminho absoluto, extrair o diretório
    if os.path.isabs(db_path):
        db_dir = Path(db_path).parent
    else:
        # Se for relativo, usar diretório atual
        db_dir = Path.cwd()
    
    # Criar diretório de dados se não existir
    try:
        db_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Diretório de dados garantido: {db_dir}")
    except Exception as e:
        print(f"✗ Erro ao criar diretório {db_dir}: {e}", file=sys.stderr)
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
    
    # Verificar permissões de escrita
    try:
        test_file = db_dir / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        print(f"✓ Permissões de escrita OK em {db_dir}")
    except Exception as e:
        print(f"✗ Sem permissão de escrita em {db_dir}: {e}", file=sys.stderr)
        sys.exit(1)
    
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
