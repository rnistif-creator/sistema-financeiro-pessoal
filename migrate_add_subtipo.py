"""
Script de migração para adicionar coluna subtipo_lancamento_id na tabela lancamentos
"""
import sqlite3
from pathlib import Path

DB_PATH = "lancamentos.db"

def migrate():
    """Adiciona coluna subtipo_lancamento_id na tabela lancamentos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(lancamentos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'subtipo_lancamento_id' in columns:
            print("✓ Coluna subtipo_lancamento_id já existe na tabela lancamentos")
        else:
            # Adicionar a coluna
            print("Adicionando coluna subtipo_lancamento_id...")
            cursor.execute("""
                ALTER TABLE lancamentos 
                ADD COLUMN subtipo_lancamento_id INTEGER
            """)
            
            # Criar índice para a nova coluna
            print("Criando índice...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_lancamentos_subtipo 
                ON lancamentos(subtipo_lancamento_id)
            """)
            
            conn.commit()
            print("✓ Migração concluída com sucesso!")
            print("  - Coluna subtipo_lancamento_id adicionada")
            print("  - Índice idx_lancamentos_subtipo criado")
    
    except Exception as e:
        print(f"✗ Erro na migração: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("MIGRAÇÃO: Adicionar suporte a subtipos em lançamentos")
    print("="*60)
    migrate()
    print("="*60)
