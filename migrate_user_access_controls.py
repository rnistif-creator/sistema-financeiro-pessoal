"""
Migração: adicionar colunas de controle de acesso em users
- acesso_ate DATE NULL
- acesso_indeterminado BOOLEAN NOT NULL DEFAULT 0
- bloqueado_financeiro BOOLEAN NOT NULL DEFAULT 0
"""
import sqlite3
from pathlib import Path

DB_PATH = "lancamentos.db"

def column_exists(cursor, table: str, col: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cursor.fetchall())

def migrate():
    if not Path(DB_PATH).exists():
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return False
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        print("🔧 Iniciando migração de controle de acesso de usuários...")
        added = False
        if not column_exists(cur, 'users', 'acesso_ate'):
            cur.execute("ALTER TABLE users ADD COLUMN acesso_ate DATE")
            print("  ✓ Coluna acesso_ate adicionada")
            added = True
        else:
            print("  ℹ️  Coluna acesso_ate já existe")
        if not column_exists(cur, 'users', 'acesso_indeterminado'):
            cur.execute("ALTER TABLE users ADD COLUMN acesso_indeterminado BOOLEAN NOT NULL DEFAULT 0")
            print("  ✓ Coluna acesso_indeterminado adicionada")
            added = True
        else:
            print("  ℹ️  Coluna acesso_indeterminado já existe")
        if not column_exists(cur, 'users', 'bloqueado_financeiro'):
            cur.execute("ALTER TABLE users ADD COLUMN bloqueado_financeiro BOOLEAN NOT NULL DEFAULT 0")
            print("  ✓ Coluna bloqueado_financeiro adicionada")
            added = True
        else:
            print("  ℹ️  Coluna bloqueado_financeiro já existe")
        if added:
            conn.commit()
            print("✅ Migração concluída!")
        else:
            print("✅ Nada a migrar.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro na migração: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
