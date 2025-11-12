# Imagem base oficial do Python 3.11 slim (menor e mais segura)
FROM python:3.11-slim

# Metadados da imagem
LABEL maintainer="Ricardo"
LABEL description="Sistema Financeiro Pessoal - FastAPI + SQLAlchemy"
LABEL version="1.0"

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Variáveis de ambiente para otimizar Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema necessárias
# (útil se precisar de compilações nativas)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas requirements.txt primeiro (cache layer)
# Se as dependências não mudarem, Docker reusa essa camada
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY app/ ./app/
COPY init_db.py .
COPY diagnose.py .
COPY generate_icons.py .

# Criar diretórios necessários
RUN mkdir -p backups app/static/icons

# Gerar ícones do PWA
RUN python generate_icons.py

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Expor porta da aplicação
EXPOSE 8001

# Healthcheck para verificar se o container está saudável
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/api/health')" || exit 1

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
