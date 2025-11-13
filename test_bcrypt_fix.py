"""
Teste para verificar se o bcrypt está funcionando com truncamento
"""
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__truncate_error=False
)

def get_password_hash(password: str) -> str:
    """Gera hash bcrypt da senha"""
    print(f"Senha original: {len(password)} caracteres, {len(password.encode('utf-8'))} bytes")
    return pwd_context.hash(password)

# Teste 1: Senha curta
print("\n=== Teste 1: Senha curta ===")
try:
    hash1 = get_password_hash("Teste@123")
    print(f"✓ Hash gerado com sucesso")
except Exception as e:
    print(f"✗ Erro: {e}")

# Teste 2: Senha longa (50 caracteres)
print("\n=== Teste 2: Senha longa (50 chars) ===")
try:
    senha_longa = "A" * 40 + "@123456789"
    hash2 = get_password_hash(senha_longa)
    print(f"✓ Hash gerado com sucesso")
except Exception as e:
    print(f"✗ Erro: {e}")

# Teste 3: Senha muito longa (100 caracteres)
print("\n=== Teste 3: Senha muito longa (100 chars) ===")
try:
    senha_muito_longa = "A" * 90 + "@123456789"
    hash3 = get_password_hash(senha_muito_longa)
    print(f"✓ Hash gerado com sucesso")
except Exception as e:
    print(f"✗ Erro: {e}")

print("\n=== Testes concluídos ===")
