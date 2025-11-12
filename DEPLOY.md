# 🚀 Deploy - Sistema Financeiro Pessoal

Este guia explica como fazer deploy da aplicação no GitHub e em diversas plataformas cloud.

---

## 📋 Pré-requisitos

- Conta no [GitHub](https://github.com)
- Git instalado localmente
- Conta em uma plataforma cloud (escolha uma):
  - [Railway](https://railway.app) (recomendado - mais simples)
  - [Render](https://render.com) (free tier generoso)
  - [Fly.io](https://fly.io) (infraestrutura global)

---

## 1️⃣ Preparar Repositório Git

### Inicializar Git (se ainda não foi feito)

```bash
cd "C:\Users\Ricardo\Documents\Programação\Sistema financeiro pessoal"
git init
git add .
git commit -m "Initial commit - Sistema Financeiro Pessoal"
```

### Criar Repositório no GitHub

1. Acesse https://github.com/new
2. Nome do repositório: `sistema-financeiro-pessoal`
3. **Não** adicione README, .gitignore ou license (já temos localmente)
4. Clique em "Create repository"

### Conectar e Enviar para GitHub

```bash
# Substitua SEU-USUARIO pelo seu username do GitHub
git remote add origin https://github.com/SEU-USUARIO/sistema-financeiro-pessoal.git
git branch -M main
git push -u origin main
```

---

## 2️⃣ Deploy no Railway (Recomendado)

### Vantagens
- ✅ Setup automático
- ✅ 500h grátis por mês
- ✅ Deploy em segundos
- ✅ Domínio HTTPS gratuito

### Passos

1. **Acesse:** https://railway.app
2. **Login:** Com sua conta GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Selecione:** `sistema-financeiro-pessoal`
5. **Configure Variáveis de Ambiente:**
   - Clique em **Variables**
   - Adicione:
     ```
     SECRET_KEY=<gere-um-valor-aleatorio-forte>
     ENVIRONMENT=production
     LOG_LEVEL=info
     DB_PATH=/app/data/lancamentos.db
     PORT=8000
     ```
   
6. **Deploy automático** será iniciado
7. **Domínio:** Railway gera um domínio automático (ex: `app-name.railway.app`)

### Gerar SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Persistência de Dados

Railway suporta volumes persistentes:
- Vá em **Settings** → **Volumes**
- Crie um volume apontando para `/app/data`

---

## 3️⃣ Deploy no Render

### Vantagens
- ✅ Free tier permanente
- ✅ Disco persistente incluído
- ✅ Auto-deploy no push

### Passos

1. **Acesse:** https://render.com
2. **Login:** Com GitHub
3. **New** → **Web Service**
4. **Conecte:** Seu repositório `sistema-financeiro-pessoal`
5. **Configure:**
   - **Name:** `sistema-financeiro-pessoal`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables:**
   ```
   SECRET_KEY=<gere-um-valor-aleatorio-forte>
   ENVIRONMENT=production
   LOG_LEVEL=info
   DB_PATH=/opt/render/project/src/data/lancamentos.db
   ```
7. **Adicionar Disco Persistente:**
   - Em **Settings** → **Disks**
   - **Add Disk:**
     - Name: `data`
     - Mount Path: `/opt/render/project/src/data`
     - Size: `1 GB` (free tier)

### Deploy com render.yaml

Alternativamente, o arquivo `render.yaml` já está configurado:
- Render detecta automaticamente
- Faz deploy seguindo as especificações do arquivo

---

## 4️⃣ Deploy no Fly.io

### Vantagens
- ✅ Infraestrutura global
- ✅ 3 VMs gratuitas
- ✅ CLI poderosa

### Instalação da CLI

**Windows (PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Linux/Mac:**
```bash
curl -L https://fly.io/install.sh | sh
```

### Passos

1. **Login:**
   ```bash
   fly auth login
   ```

2. **Criar App (o fly.toml já está configurado):**
   ```bash
   fly launch --no-deploy
   ```
   - Escolha um nome para o app
   - Região: `gru` (São Paulo) ou `iad` (Virginia)

3. **Criar Volume Persistente:**
   ```bash
   fly volumes create data --size 1
   ```

4. **Configurar Secrets:**
   ```bash
   fly secrets set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   fly secrets set ENVIRONMENT=production
   ```

5. **Deploy:**
   ```bash
   fly deploy
   ```

6. **Abrir App:**
   ```bash
   fly open
   ```

---

## 🔧 Variáveis de Ambiente (Resumo)

### Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta JWT (32+ chars) | `abc123...xyz` |
| `ENVIRONMENT` | Ambiente de execução | `production` |
| `DB_PATH` | Caminho do banco SQLite | `/app/data/lancamentos.db` |
| `PORT` | Porta do servidor | `8000` |

### Opcionais

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `LOG_LEVEL` | Nível de log | `info` |
| `HOST` | Host do servidor | `0.0.0.0` |
| `JWT_ALGORITHM` | Algoritmo JWT | `HS256` |
| `JWT_EXPIRATION_MINUTES` | Expiração token | `1440` |

---

## 🧪 Testar Deploy Localmente

### Com Docker

```bash
# Build
docker build -f Dockerfile.production -t financeiro-app .

# Run
docker run -p 8000:8000 \
  -e SECRET_KEY="test-secret-key-for-local" \
  -e ENVIRONMENT="development" \
  -v $(pwd)/data:/app/data \
  financeiro-app
```

### Sem Docker

```bash
# Ativar venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Linux/Mac

# Configurar env
$env:SECRET_KEY="test-secret-key"
$env:ENVIRONMENT="production"
$env:PORT="8000"

# Rodar
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Acesse: http://localhost:8000

---

## 🔄 CI/CD Automático

Após o deploy inicial, **pushes para `main`** fazem deploy automático:

```bash
# Fazer mudanças
git add .
git commit -m "Sua mensagem"
git push origin main

# A plataforma cloud fará deploy automaticamente
```

---

## 📊 Monitoramento

### Health Check

Todas as plataformas verificam automaticamente:
- `GET /health` - Status básico
- `GET /api/health` - Status detalhado com DB

### Logs

**Railway:**
```
Dashboard → Logs tab
```

**Render:**
```
Dashboard → Logs
```

**Fly.io:**
```bash
fly logs
```

---

## 🗄️ Banco de Dados

### SQLite em Produção

A aplicação usa SQLite por padrão (simples e sem necessidade de servidor DB separado).

**Vantagens:**
- ✅ Zero configuração
- ✅ Incluído no deploy
- ✅ Backups simples

**Limitações:**
- ⚠️ Não recomendado para alta concorrência (>100 usuários simultâneos)

### Migrar para PostgreSQL (Futuro)

Se crescer, considere PostgreSQL:

1. **Adicionar ao `requirements.txt`:**
   ```
   psycopg2-binary>=2.9.9
   ```

2. **Atualizar `app/main.py`:**
   ```python
   DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
   ```

3. **Configurar `DATABASE_URL` na plataforma:**
   - Railway: Add PostgreSQL plugin (automático)
   - Render: Add PostgreSQL database (automático)
   - Fly.io: `fly postgres create`

---

## 🔐 Segurança

### Checklist Produção

- ✅ `SECRET_KEY` forte e aleatória
- ✅ `.env` no `.gitignore`
- ✅ HTTPS habilitado (automático nas plataformas)
- ✅ Backups regulares configurados
- ✅ Logs de acesso habilitados

### Gerar SECRET_KEY Forte

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## 🆘 Troubleshooting

### Erro: "Application failed to start"

1. Verifique logs da plataforma
2. Confirme que `SECRET_KEY` está configurada
3. Valide `requirements.txt` está completo

### Erro: "Database locked"

- SQLite não suporta alta concorrência
- Considere migrar para PostgreSQL

### Disco cheio

1. **Railway/Render:** Aumente o tamanho do volume
2. **Fly.io:** `fly volumes extend <volume-id> --size <new-size>`
3. Configure limpeza automática de backups antigos

---

## 📚 Recursos Adicionais

- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## ✅ Checklist Final

Antes do primeiro deploy:

- [ ] Repositório no GitHub criado e atualizado
- [ ] `.gitignore` configurado (não commitar `.env`, `*.db`)
- [ ] `SECRET_KEY` gerada e configurada na plataforma
- [ ] Variáveis de ambiente configuradas
- [ ] Disco persistente criado para `/app/data`
- [ ] Health check funcionando (`/health`)
- [ ] Primeiro deploy realizado com sucesso
- [ ] Teste login e funcionalidades básicas
- [ ] Configurar domínio customizado (opcional)

---

**Pronto!** 🎉 Sua aplicação está no ar!
