"""
Script para rodar o servidor diretamente via Python
Útil para debug quando uvicorn apresenta problemas
Carrega variáveis de ambiente de um arquivo .env se existir.
"""
if __name__ == "__main__":
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        pass
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
