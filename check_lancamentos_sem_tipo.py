#!/usr/bin/env python3
"""
Script para verificar lançamentos sem tipo_lancamento_id
"""
from app.main import SessionLocal, Lancamento, User

def main():
    db = SessionLocal()
    try:
        # Verificar usuários
        users = db.query(User).all()
        print(f"📊 Total de usuários: {len(users)}\n")
        
        for user in users:
            print(f"👤 Usuário: {user.nome} ({user.email})")
            
            # Lançamentos sem tipo
            lancamentos_sem_tipo = db.query(Lancamento).filter(
                Lancamento.usuario_id == user.id,
                Lancamento.tipo_lancamento_id == None
            ).all()
            
            print(f"   Lançamentos sem tipo: {len(lancamentos_sem_tipo)}")
            
            if lancamentos_sem_tipo:
                print("\n   Detalhes:")
                for l in lancamentos_sem_tipo:
                    print(f"   - ID {l.id}: {l.tipo.upper()} | {l.fornecedor} | R$ {l.valor_total} | {l.data_lancamento}")
            
            print()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
