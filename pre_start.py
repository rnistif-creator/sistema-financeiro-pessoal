#!/usr/bin/env python3
"""
Script de pré-inicialização para Render
Garante que diretórios necessários existem antes de iniciar o servidor
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Opcional: criação automática de admin em ambientes (staging/produção) usando variáveis de ambiente.
# Para ativar defina: INITIAL_ADMIN_EMAIL, INITIAL_ADMIN_PASSWORD, INITIAL_ADMIN_NAME (opcional)
def maybe_create_initial_admin():
    # Regras de segurança:
    # 1. Apenas roda em ENVIRONMENT=staging ou dev.
    # 2. Requer flag explícita INITIAL_ADMIN_ENABLE=1.
    # 3. Exige email e password.
    # 4. Limpa variáveis sensíveis da memória do processo após uso.
    env = os.getenv("ENVIRONMENT", "").lower()
    if env not in {"staging", "dev"}:
        return
    if os.getenv("INITIAL_ADMIN_ENABLE") != "1":
        return
    email = os.getenv("INITIAL_ADMIN_EMAIL")
    password = os.getenv("INITIAL_ADMIN_PASSWORD")
    force_reset = os.getenv("INITIAL_ADMIN_FORCE_RESET") == "1"
    name = os.getenv("INITIAL_ADMIN_NAME", "Admin")
    if not email or not password:
        return
    try:
        # Importar apenas se variáveis presentes para evitar custo no cold start
        from app.main import SessionLocal, User
        from app.auth import get_user_by_email, create_user, UserCreate, get_password_hash, verify_password
        db = SessionLocal()
        try:
            user = get_user_by_email(db, email)
            if user:
                # Promover se necessário
                if not user.admin:
                    user.admin = True
                    db.commit()
                    print(f"✓ Usuário existente promovido a admin: {email}")
                # Forçar reset para senha padrão fraca se solicitado
                if force_reset or verify_password('123456', user.senha_hash) or password == '123456':
                    if password == '123456' or force_reset:
                        user.senha_hash = get_password_hash('123456')
                        db.commit()
                        print("✓ Senha do admin definida para padrão temporário '123456' (troca obrigatória)")
            else:
                if password == '123456':
                    # Criar usuário ignorando força (senha temporária obrigatória)
                    hashed = get_password_hash('123456')
                    new_user = User(
                        email=email,
                        nome=name,
                        senha_hash=hashed,
                        admin=True,
                        ativo=True,
                        created_at=datetime.utcnow()
                    )
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)
                    print(f"✓ Admin inicial criado com senha temporária fraca '123456': {new_user.email} (id={new_user.id})")
                else:
                    # Caminho normal (senha forte exige requisitos)
                    created = create_user(db, UserCreate(email=email, nome=name, password=password), is_admin=True)
                    print(f"✓ Admin inicial criado: {created.email} (id={created.id})")
        finally:
            db.close()
            # Limpar variáveis sensíveis para reduzir chance de exposição acidental em logs futuros
            for var in ("INITIAL_ADMIN_PASSWORD", "INITIAL_ADMIN_EMAIL", "INITIAL_ADMIN_NAME"):
                os.environ.pop(var, None)
    except Exception as e:
        print(f"✗ Falha ao criar admin inicial: {e}")

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
    # Criar admin inicial se configurado
    maybe_create_initial_admin()
    print("✓ Pronto para iniciar o servidor\n")
