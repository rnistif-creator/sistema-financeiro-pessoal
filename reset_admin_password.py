#!/usr/bin/env python3
"""
Script para resetar senha do admin para 123456.
Uso: python reset_admin_password.py
"""
import sys
from app.main import SessionLocal, User
from app.auth import get_password_hash

def reset_admin_password():
    """Reseta senha do admin ricardo@rfinance.com.br para 123456"""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == 'ricardo@rfinance.com.br').first()
        
        if not admin:
            print("❌ Usuário admin ricardo@rfinance.com.br não encontrado.")
            print("   Criando novo admin...")
            admin = User(
                email='ricardo@rfinance.com.br',
                nome='Ricardo Admin',
                senha_hash=get_password_hash('123456'),
                admin=True,
                ativo=True
            )
            db.add(admin)
        else:
            print(f"✓ Admin encontrado: {admin.nome} ({admin.email})")
            admin.senha_hash = get_password_hash('123456')
            admin.admin = True
            admin.ativo = True
        
        db.commit()
        print("✅ Senha resetada para: 123456")
        print(f"   Email: {admin.email}")
        print(f"   Admin: {admin.admin}")
        print(f"   Ativo: {admin.ativo}")
        return 0
        
    except Exception as e:
        print(f"❌ Erro ao resetar senha: {e}")
        db.rollback()
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(reset_admin_password())
