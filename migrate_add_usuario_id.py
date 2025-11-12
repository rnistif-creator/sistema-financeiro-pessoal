"""
Migração: Adicionar coluna usuario_id em todas as tabelas principais
e popular com o ID do primeiro usuário (admin)
"""
import sqlite3
from pathlib import Path

DB_PATH = "lancamentos.db"

def migrate():
    print("=== Iniciando migração: adicionar usuario_id ===\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar se existe pelo menos um usuário
        cursor.execute("SELECT id FROM users WHERE admin = 1 LIMIT 1")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("❌ Nenhum usuário admin encontrado no banco!")
            print("   Execute init_db.py primeiro para criar o usuário admin.")
            return False
        
        admin_id = admin_user[0]
        print(f"✓ Usuário admin encontrado: ID {admin_id}\n")
        
        # 2. Adicionar coluna usuario_id em cada tabela (se não existir)
        tables_to_migrate = [
            "lancamentos",
            "parcelas",
            "formas_pagamento",
            "tipos_lancamentos",
            "subtipos_lancamentos",
            "lancamentos_recorrentes"
        ]
        
        # Verificar se tabela metas existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metas'")
        if cursor.fetchone():
            tables_to_migrate.append("metas")
        
        for table in tables_to_migrate:
            print(f"Processando tabela: {table}")
            
            # Verificar se coluna já existe
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if "usuario_id" in columns:
                print(f"  ⚠ Coluna usuario_id já existe em {table}")
                continue
            
            # Adicionar coluna usuario_id (nullable temporariamente)
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN usuario_id INTEGER")
            print(f"  ✓ Coluna usuario_id adicionada")
            
            # Popular com ID do admin
            cursor.execute(f"UPDATE {table} SET usuario_id = ?", (admin_id,))
            affected = cursor.rowcount
            print(f"  ✓ {affected} registro(s) atualizado(s) com usuario_id = {admin_id}")
            
            # Em SQLite não podemos adicionar NOT NULL diretamente após ALTER TABLE
            # Mas podemos verificar se todos os registros foram populados
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE usuario_id IS NULL")
            nulls = cursor.fetchone()[0]
            if nulls > 0:
                print(f"  ⚠ Atenção: {nulls} registro(s) com usuario_id NULL em {table}")
            
            print()
        
        # 3. Criar índices para melhor performance
        print("Criando índices para usuario_id...")
        for table in tables_to_migrate:
            index_name = f"idx_{table}_usuario_id"
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}(usuario_id)")
                print(f"  ✓ Índice criado: {index_name}")
            except sqlite3.OperationalError as e:
                if "already exists" not in str(e):
                    print(f"  ⚠ Erro ao criar índice {index_name}: {e}")
        
        conn.commit()
        print("\n✅ Migração concluída com sucesso!")
        print(f"   Todos os registros foram associados ao usuário ID {admin_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if not Path(DB_PATH).exists():
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        print("   Execute init_db.py primeiro.")
    else:
        success = migrate()
        exit(0 if success else 1)
