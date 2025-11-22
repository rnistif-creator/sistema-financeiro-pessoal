"""Teste de inicialização do servidor com captura de erros detalhada"""
import sys
import os
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Forçar UTF-8 no Windows para evitar problemas com símbolos
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

print("Iniciando servidor de teste...\n")

try:
    import uvicorn
    from app.main import app
    
    # Configurar uvicorn com log detalhado
    port = int(os.getenv("PORT", "8001"))
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=port,
        log_level="debug",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    
    print("[OK] Servidor configurado")
    print(f"[OK] Iniciando em http://127.0.0.1:{port}")
    print("\nPressione Ctrl+C para parar\n")
    
    server.run()
    
except KeyboardInterrupt:
    print("\n\n[OK] Servidor parado pelo usuario")
except Exception as e:
    print(f"\n[ERRO] ERRO ao iniciar servidor:")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    print("\nTraceback completo:")
    traceback.print_exc()
    sys.exit(1)
