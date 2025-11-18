#!/usr/bin/env python3
"""
Script utilitário para desbloquear conta admin após tentativas falhas
"""
import sys
import argparse
from datetime import datetime
from app.main import SessionLocal, LoginAttempt

def unblock_admin(email: str):
    """Remove bloqueio temporário de conta admin"""
    db = SessionLocal()
    try:
        # Buscar tentativas bloqueadas
        blocked = db.query(LoginAttempt).filter(
            LoginAttempt.email == email,
            LoginAttempt.is_admin_attempt == True,
            LoginAttempt.blocked_until != None,
            LoginAttempt.blocked_until > datetime.utcnow()
        ).all()
        
        if not blocked:
            print(f"✓ Conta {email} não está bloqueada")
            return
        
        # Limpar bloqueios
        for attempt in blocked:
            attempt.blocked_until = None
        
        db.commit()
        print(f"✓ {len(blocked)} bloqueio(s) removido(s) para {email}")
        print("  A conta pode fazer login novamente")
        
    except Exception as e:
        print(f"✗ Erro: {e}")
        sys.exit(1)
    finally:
        db.close()

def list_blocked_accounts():
    """Lista todas as contas atualmente bloqueadas"""
    db = SessionLocal()
    try:
        blocked = db.query(LoginAttempt).filter(
            LoginAttempt.blocked_until != None,
            LoginAttempt.blocked_until > datetime.utcnow()
        ).order_by(LoginAttempt.email, LoginAttempt.blocked_until.desc()).all()
        
        if not blocked:
            print("✓ Nenhuma conta bloqueada no momento")
            return
        
        print(f"\n⚠️  {len(blocked)} conta(s) bloqueada(s):\n")
        seen = set()
        for attempt in blocked:
            key = (attempt.email, attempt.is_admin_attempt)
            if key in seen:
                continue
            seen.add(key)
            
            tipo = "ADMIN" if attempt.is_admin_attempt else "USER"
            remaining = (attempt.blocked_until - datetime.utcnow()).total_seconds() / 60
            print(f"  [{tipo}] {attempt.email}")
            print(f"    Bloqueado até: {attempt.blocked_until.strftime('%d/%m/%Y %H:%M')}")
            print(f"    Tempo restante: {int(remaining)} minutos")
            print(f"    IP: {attempt.ip_address}")
            print()
    
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Gerenciar bloqueios de tentativas de login")
    parser.add_argument("--unblock", help="Desbloquear conta por email")
    parser.add_argument("--list", action="store_true", help="Listar contas bloqueadas")
    
    args = parser.parse_args()
    
    if args.list:
        list_blocked_accounts()
    elif args.unblock:
        unblock_admin(args.unblock)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
