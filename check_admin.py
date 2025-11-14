#!/usr/bin/env python3
"""Script rápido para verificar e resetar admin com senha 123456"""
from app.main import SessionLocal, User
from app.auth import verify_password, get_password_hash

db = SessionLocal()
try:
    admins = db.query(User).filter(User.admin == True).all()
    
    if not admins:
        print("❌ Nenhum admin encontrado no banco.")
    else:
        print(f"✓ Encontrados {len(admins)} admin(s):\n")
        for u in admins:
            test_weak = False
            try:
                test_weak = verify_password('123456', u.senha_hash)
            except Exception as e:
                print(f"  ⚠️  Erro ao testar senha: {e}")
            
            print(f"  ID: {u.id}")
            print(f"  Email: {u.email}")
            print(f"  Nome: {u.nome}")
            print(f"  Admin: {u.admin}")
            print(f"  Ativo: {u.ativo}")
            print(f"  Senha é '123456': {test_weak}")
            print(f"  Hash (30 chars): {u.senha_hash[:30]}...")
            print()
            
            if not test_weak:
                print("  ⚠️  Senha atual NÃO é 123456")
                resp = input("  Resetar para 123456? (s/N): ").strip().lower()
                if resp == 's':
                    u.senha_hash = get_password_hash('123456')
                    db.commit()
                    print("  ✓ Senha resetada para 123456\n")
                else:
                    print("  ✗ Senha não alterada\n")
finally:
    db.close()

print("Concluído.")
