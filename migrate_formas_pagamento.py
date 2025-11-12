"""
Script de migração para adicionar formas de pagamento
Adiciona:
- Tabela formas_pagamento
- Campos forma_pagamento_id e observacao_pagamento em parcelas
"""
import sqlite3
from datetime import date

# Caminho do banco de dados
DB_PATH = "lancamentos.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 Iniciando migração...")
    
    try:
        # Verificar se a tabela formas_pagamento já existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='formas_pagamento'
        """)
        
        if not cursor.fetchone():
            print("  ➕ Criando tabela formas_pagamento...")
            cursor.execute("""
                CREATE TABLE formas_pagamento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome VARCHAR(100) NOT NULL,
                    tipo VARCHAR(20) NOT NULL,
                    banco VARCHAR(100),
                    limite_credito NUMERIC(14,2),
                    ativo BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATE NOT NULL,
                    observacao VARCHAR(500)
                )
            """)
            print("  ✅ Tabela formas_pagamento criada!")
            
            # Adicionar formas de pagamento padrão
            print("  ➕ Adicionando formas de pagamento padrão...")
            formas_padrao = [
                ("Dinheiro", "dinheiro", None, None, 1, date.today().isoformat(), "Pagamento em dinheiro físico"),
                ("PIX", "pix", None, None, 1, date.today().isoformat(), "Transferência via PIX"),
            ]
            
            cursor.executemany("""
                INSERT INTO formas_pagamento (nome, tipo, banco, limite_credito, ativo, created_at, observacao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, formas_padrao)
            print(f"  ✅ {len(formas_padrao)} formas padrão adicionadas!")
        else:
            print("  ℹ️  Tabela formas_pagamento já existe")
        
        # Verificar se as colunas já existem na tabela parcelas
        cursor.execute("PRAGMA table_info(parcelas)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        
        if 'forma_pagamento_id' not in colunas_existentes:
            print("  ➕ Adicionando coluna forma_pagamento_id em parcelas...")
            cursor.execute("""
                ALTER TABLE parcelas 
                ADD COLUMN forma_pagamento_id INTEGER
            """)
            print("  ✅ Coluna forma_pagamento_id adicionada!")
        else:
            print("  ℹ️  Coluna forma_pagamento_id já existe")
        
        if 'observacao_pagamento' not in colunas_existentes:
            print("  ➕ Adicionando coluna observacao_pagamento em parcelas...")
            cursor.execute("""
                ALTER TABLE parcelas 
                ADD COLUMN observacao_pagamento VARCHAR(500)
            """)
            print("  ✅ Coluna observacao_pagamento adicionada!")
        else:
            print("  ℹ️  Coluna observacao_pagamento já existe")
        
        conn.commit()
        print("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erro durante a migração: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
