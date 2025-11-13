"""
Teste direto com bcrypt (sem passlib)
"""
import bcrypt

def test_bcrypt_direct():
    senha = "Teste@123"
    print(f"Senha: {senha} ({len(senha)} chars, {len(senha.encode('utf-8'))} bytes)")
    
    # Bcrypt aceita bytes
    senha_bytes = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_result = bcrypt.hashpw(senha_bytes, salt)
    
    print(f"✓ Hash gerado: {hash_result[:30]}...")
    
    # Verificar
    if bcrypt.checkpw(senha_bytes, hash_result):
        print("✓ Senha verificada com sucesso!")
    else:
        print("✗ Falha na verificação")

print("=== Teste direto com bcrypt ===")
test_bcrypt_direct()
