# 🎯 Comandos Úteis - Cheat Sheet

Referência rápida de comandos para deploy e manutenção.

---

## 🚀 Deploy

### Inicializar Git e Enviar para GitHub

```powershell
# Windows
.\setup-git.ps1

# Linux/Mac
chmod +x setup-git.sh && ./setup-git.sh
```

### Gerar SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Railway

```bash
# Via interface web
# 1. https://railway.app
# 2. New Project → Deploy from GitHub
# 3. Configure env vars
# 4. Deploy automático
```

### Render

```bash
# Via interface web (render.yaml auto-detectado)
# 1. https://render.com
# 2. New Web Service
# 3. Connect repository
# 4. Deploy automático
```

### Fly.io

```bash
# Instalar CLI
iwr https://fly.io/install.ps1 -useb | iex  # Windows
# curl -L https://fly.io/install.sh | sh    # Linux/Mac

# Deploy
fly auth login
fly launch --no-deploy
fly volumes create data --size 1
fly secrets set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
fly deploy
fly open
```

---

## 🧪 Desenvolvimento Local

### Setup Inicial

```bash
# Clonar
git clone https://github.com/SEU-USUARIO/sistema-financeiro-pessoal.git
cd sistema-financeiro-pessoal

# Ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Linux/Mac

# Dependências
pip install -r requirements.txt

# Configurar
copy .env.example .env
# Editar .env: SECRET_KEY, etc.

# Inicializar DB
python init_db.py
```

### Rodar Servidor

```bash
# Modo desenvolvimento
python start_server.py

# Ou com reload
uvicorn app.main:app --reload --port 8000

# Com variáveis de ambiente
$env:SECRET_KEY="test-key"; $env:PORT="8000"; python start_server.py
```

### Testes

```bash
# Todos os testes
python run_tests.py

# Com pytest
pytest -v

# Teste específico
pytest tests/test_dashboard.py -v

# Com coverage
pytest --cov=app tests/

# Limpar cache
pytest --cache-clear
```

---

## 🗄️ Banco de Dados

### Inicializar

```bash
python init_db.py
```

### Resetar (cuidado!)

```bash
python reset_db.py
```

### Backup Manual

```python
python -c "from app.main import criar_backup; print(criar_backup())"
```

### Seed Demo Data

```bash
python seed_demo_data.py
```

### Listar Backups

```powershell
Get-ChildItem backups/ | Sort-Object LastWriteTime -Descending | Select-Object -First 10
```

---

## 📊 Git

### Workflow Básico

```bash
# Status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "feat: sua mensagem"

# Push
git push origin main

# Pull (atualizar)
git pull origin main
```

### Branches

```bash
# Criar branch
git checkout -b feature/nova-funcionalidade

# Mudar de branch
git checkout main

# Listar branches
git branch -a

# Merge
git checkout main
git merge feature/nova-funcionalidade

# Deletar branch
git branch -d feature/nova-funcionalidade
```

### Desfazer Mudanças

```bash
# Descartar mudanças locais
git checkout -- <arquivo>

# Desfazer último commit (mantém arquivos)
git reset --soft HEAD~1

# Desfazer último commit (descarta mudanças)
git reset --hard HEAD~1

# Reverter commit (cria novo commit)
git revert HEAD
```

---

## 🐳 Docker

### Build

```bash
docker build -f Dockerfile.production -t financeiro-app .
```

### Run

```bash
docker run -p 8000:8000 \
  -e SECRET_KEY="test-secret-key" \
  -e ENVIRONMENT="production" \
  -v $(pwd)/data:/app/data \
  financeiro-app
```

### Docker Compose (se criar)

```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

## 🔍 Debug

### Logs da Aplicação

```bash
# Desenvolvimento
python start_server.py

# Produção - Railway
# Dashboard → Logs tab

# Produção - Render
# Dashboard → Logs

# Produção - Fly.io
fly logs
fly logs --app financeiro-prod
```

### Testar Endpoints

```bash
# Health check
curl http://localhost:8000/health
curl http://localhost:8000/api/health

# Com autenticação
curl -H "Authorization: Bearer SEU_TOKEN" http://localhost:8000/api/dashboard
```

### Debug Python

```python
# Adicionar breakpoint no código
import pdb; pdb.set_trace()

# Ou usar breakpoint() (Python 3.7+)
breakpoint()
```

---

## 📦 Dependências

### Atualizar Dependências

```bash
# Atualizar todas
pip install --upgrade -r requirements.txt

# Atualizar específica
pip install --upgrade fastapi

# Gerar novo requirements.txt
pip freeze > requirements.txt
```

### Verificar Vulnerabilidades

```bash
pip install safety
safety check
```

---

## 🌍 Ambientes Múltiplos

### Criar Branch Staging

```bash
git checkout -b develop
git push origin develop

# Configurar deploy de develop → staging na plataforma
```

### Variáveis por Ambiente

**Development:**
```bash
SECRET_KEY=dev-key
ENVIRONMENT=development
LOG_LEVEL=debug
```

**Staging:**
```bash
SECRET_KEY=staging-key-abc123
ENVIRONMENT=staging
LOG_LEVEL=info
```

**Production:**
```bash
SECRET_KEY=prod-key-xyz789-super-secret
ENVIRONMENT=production
LOG_LEVEL=warning
```

---

## 🔐 Segurança

### Gerar Chaves

```bash
# SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Hash de senha (bcrypt)
python -c "from passlib.hash import bcrypt; print(bcrypt.hash('senha123'))"
```

### Verificar Secrets no Código

```bash
# Procurar por possíveis secrets expostos
git grep -i "password\|secret\|api.key"
```

### Atualizar Dependências de Segurança

```bash
pip install --upgrade passlib python-jose
```

---

## 📊 Monitoramento

### Health Checks

```bash
# Local
curl http://localhost:8000/health

# Produção
curl https://seu-app.railway.app/health
```

### Status do Servidor

**Railway:**
```bash
# Via web dashboard
```

**Fly.io:**
```bash
fly status
fly status --app financeiro-prod
```

**Render:**
```bash
# Via web dashboard
```

---

## 🔄 CI/CD

### Deploy Automático

```bash
# Push para main → Deploy em produção
git push origin main

# Push para develop → Deploy em staging
git push origin develop
```

### Rollback

**Git:**
```bash
git revert HEAD
git push origin main
```

**Railway/Render:**
```
Dashboard → Deployments → [Deploy anterior] → Redeploy
```

**Fly.io:**
```bash
fly releases
fly releases rollback <version>
```

---

## 📝 Manutenção

### Limpar Cache Python

```bash
# Remover __pycache__
Get-ChildItem -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force

# Ou em Linux/Mac
find . -type d -name __pycache__ -exec rm -r {} +
```

### Limpar Backups Antigos

```powershell
# Manter apenas últimos 30 backups
Get-ChildItem backups/*.db | 
  Sort-Object LastWriteTime -Descending | 
  Select-Object -Skip 30 | 
  Remove-Item
```

### Otimizar Banco SQLite

```python
python -c "import sqlite3; conn = sqlite3.connect('lancamentos.db'); conn.execute('VACUUM'); conn.close(); print('✓ DB otimizado')"
```

---

## 🆘 Troubleshooting Rápido

### App não inicia

```bash
# Verificar imports
python -c "from app.main import app; print('✓ OK')"

# Verificar SECRET_KEY
echo $env:SECRET_KEY  # Windows
# echo $SECRET_KEY    # Linux/Mac

# Verificar porta
netstat -ano | findstr :8000  # Windows
# lsof -i :8000                # Linux/Mac
```

### Testes falhando

```bash
# Limpar cache
pytest --cache-clear

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall

# Rodar com output verbose
pytest -vv -s
```

### Git push rejeitado

```bash
# Pull primeiro
git pull origin main --rebase

# Depois push
git push origin main
```

---

## 📚 Links Úteis

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)

---

**Salve este arquivo para referência rápida!** 📌
