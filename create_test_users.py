"""
Script para criar usuários de teste no banco de dados local
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Importar os modelos e funções necessários
from app.main import User, Base
from app.auth import get_password_hash
from datetime import datetime

# Configurar banco de dados
DB_PATH = os.getenv("DB_PATH", "lancamentos.db")
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_users():
    db = SessionLocal()
    try:
        # Verificar se usuários já existem
        user_test = db.query(User).filter(User.email == "teste@teste.com").first()
        admin_test = db.query(User).filter(User.email == "admin@admin.com").first()
        
        if user_test:
            print("✓ Usuário teste@teste.com já existe")
        else:
            # Criar usuário normal
            user = User(
                email="teste@teste.com",
                nome="Usuário Teste",
                senha_hash=get_password_hash("Teste@123456"),
                admin=False,
                ativo=True,
                created_at=datetime.utcnow()
            )
            db.add(user)
            print("✓ Criado usuário: teste@teste.com | Senha: Teste@123456")
        
        if admin_test:
            print("✓ Admin admin@admin.com já existe")
        else:
            # Criar admin
            admin = User(
                email="admin@admin.com",
                nome="Admin Teste",
                senha_hash=get_password_hash("Admin@123456"),
                admin=True,
                ativo=True,
                created_at=datetime.utcnow()
            )
            db.add(admin)
            print("✓ Criado admin: admin@admin.com | Senha: Admin@123456")
        
        db.commit()
        print("\n✅ Usuários de teste prontos!")
        print("\n📋 Credenciais:")
        print("   Usuário: teste@teste.com | Senha: Teste@123456")
        print("   Admin:   admin@admin.com | Senha: Admin@123456")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar usuários: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
