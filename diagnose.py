"""Script de diagnóstico para identificar problemas ao iniciar o servidor"""
import sys
import traceback

print("=" * 60)
print("DIAGNÓSTICO DO SERVIDOR")
print("=" * 60)

# 1. Verificar versão do Python
print(f"\n1. Python versão: {sys.version}")

# 2. Tentar importar dependências críticas
print("\n2. Verificando dependências...")
dependencies = [
    'fastapi',
    'uvicorn',
    'sqlalchemy',
    'pydantic',
    'dateutil'  # python-dateutil instala como 'dateutil'
]

missing = []
for dep in dependencies:
    try:
        __import__(dep)
        print(f"   ✓ {dep}")
    except ImportError as e:
        print(f"   ✗ {dep} - FALTANDO: {e}")
        missing.append(dep)

if missing:
    print(f"\n⚠️  DEPENDÊNCIAS FALTANDO: {', '.join(missing)}")
    print("Execute: pip install -r requirements.txt")
    sys.exit(1)

# 3. Tentar importar o app
print("\n3. Tentando importar app.main...")
try:
    from app import main
    print("   ✓ app.main importado com sucesso")
except Exception as e:
    print(f"   ✗ ERRO ao importar app.main:")
    print(traceback.format_exc())
    sys.exit(1)

# 4. Verificar se app está definido
print("\n4. Verificando objeto FastAPI...")
try:
    app = main.app
    print(f"   ✓ FastAPI app encontrado: {type(app)}")
except Exception as e:
    print(f"   ✗ ERRO: {e}")
    sys.exit(1)

# 5. Verificar rotas
print("\n5. Rotas registradas:")
try:
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append(f"   {route.path}")
    print('\n'.join(routes[:10]))  # Primeiras 10 rotas
    print(f"   ... ({len(routes)} rotas no total)")
except Exception as e:
    print(f"   ⚠️  Erro ao listar rotas: {e}")

# 6. Verificar banco de dados
print("\n6. Verificando banco de dados...")
try:
    import os
    db_path = os.getenv("DB_PATH", "lancamentos.db")
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"   ✓ Banco encontrado: {db_path} ({size} bytes)")
    else:
        print(f"   ⚠️  Banco não encontrado: {db_path}")
        print("   (Será criado automaticamente na primeira execução)")
except Exception as e:
    print(f"   ⚠️  Erro: {e}")

# 7. Verificar diretórios necessários
print("\n7. Verificando estrutura de diretórios...")
try:
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent
    
    dirs_to_check = [
        base_dir / "app",
        base_dir / "app" / "templates",
        base_dir / "app" / "static",
        base_dir / "backups"
    ]
    
    for dir_path in dirs_to_check:
        if dir_path.exists():
            print(f"   ✓ {dir_path.relative_to(base_dir)}")
        else:
            print(f"   ✗ {dir_path.relative_to(base_dir)} - FALTANDO")
except Exception as e:
    print(f"   ⚠️  Erro: {e}")

# 8. Tentar iniciar servidor (teste rápido)
print("\n8. Teste de inicialização do servidor...")
try:
    import uvicorn
    print("   ✓ uvicorn importado")
    print("\n   Tentando iniciar servidor (por favor aguarde 3 segundos)...")
    
    # Criar processo em background para testar
    import subprocess
    import time
    
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(base_dir)
    )
    
    # Aguardar 3 segundos
    time.sleep(3)
    
    # Verificar se ainda está rodando
    if proc.poll() is None:
        print("   ✓ Servidor iniciou com sucesso!")
        proc.terminate()
        proc.wait(timeout=5)
    else:
        # Capturar erro
        stdout, stderr = proc.communicate()
        print("   ✗ Servidor falhou ao iniciar!")
        print("\n   STDOUT:")
        print(stdout.decode('utf-8', errors='ignore'))
        print("\n   STDERR:")
        print(stderr.decode('utf-8', errors='ignore'))
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ ERRO no teste: {e}")
    print(traceback.format_exc())
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ DIAGNÓSTICO CONCLUÍDO - TUDO OK!")
print("=" * 60)
print("\nVocê pode iniciar o servidor normalmente:")
print("  .venv\\Scripts\\python.exe -m uvicorn app.main:app --port 8001")
