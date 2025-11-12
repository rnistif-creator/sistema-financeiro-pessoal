# 📦 Arquivos de Deploy - Resumo

Este documento lista todos os arquivos criados para deploy e suas funções.

---

## ✅ Arquivos Criados

### Configuração de Deploy

| Arquivo | Plataforma | Descrição |
|---------|-----------|-----------|
| `.gitignore` | Git | Ignora arquivos sensíveis (`.env`, `*.db`, etc.) |
| `Procfile` | Heroku/Railway | Comando de inicialização |
| `railway.json` | Railway | Configuração Railway-specific |
| `render.yaml` | Render | Deploy automático com config |
| `fly.toml` | Fly.io | Configuração Fly.io |
| `Dockerfile.production` | Docker | Build para produção otimizado |

### Documentação

| Arquivo | Descrição |
|---------|-----------|
| `DEPLOY.md` | Guia completo de deploy (todas as plataformas) |
| `QUICKSTART-DEPLOY.md` | Deploy rápido em 5 minutos |
| `ENVIRONMENTS.md` | Gestão de múltiplos ambientes |
| `README.md` | Documentação principal (atualizada) |
| `.env.example` | Template de variáveis de ambiente |

### Scripts

| Arquivo | Descrição |
|---------|-----------|
| `setup-git.ps1` | Script PowerShell para inicializar Git (Windows) |
| `setup-git.sh` | Script Bash para inicializar Git (Linux/Mac) |

---

## 🚀 Ordem de Execução Recomendada

### 1. Preparar Repositório Git

**Windows:**
```powershell
.\setup-git.ps1
```

**Linux/Mac:**
```bash
chmod +x setup-git.sh
./setup-git.sh
```

O script:
- ✅ Inicializa Git
- ✅ Adiciona todos os arquivos
- ✅ Cria commit inicial
- ✅ Conecta ao GitHub
- ✅ Faz push para remote

### 2. Escolher Plataforma

Consulte:
- **Quick Start:** `QUICKSTART-DEPLOY.md`
- **Detalhado:** `DEPLOY.md`

**Recomendações:**

| Plataforma | Melhor Para | Custo |
|-----------|------------|-------|
| **Railway** | Deploy rápido, protótipos | 500h/mês grátis |
| **Render** | Produção estável, free tier | Free tier permanente |
| **Fly.io** | Performance global | 3 VMs grátis |

### 3. Configurar Variáveis

**Mínimo obrigatório:**

```bash
SECRET_KEY=<gerar-aleatoriamente>
ENVIRONMENT=production
LOG_LEVEL=info
DB_PATH=/app/data/lancamentos.db
```

**Gerar SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Deploy

Cada plataforma:

**Railway:**
- Login → New Project → Deploy from GitHub → Configure env vars → Deploy

**Render:**
- Login → New Web Service → Connect repo → Auto-detect `render.yaml`

**Fly.io:**
```bash
fly launch
fly volumes create data --size 1
fly secrets set SECRET_KEY=<value>
fly deploy
```

---

## 🔍 Detalhes dos Arquivos

### `.gitignore`
Garante que arquivos sensíveis não sejam commitados:
- `.env` - Variáveis de ambiente locais
- `*.db` - Bancos SQLite
- `__pycache__/` - Cache Python
- `.venv/` - Ambiente virtual
- `backups/` - Backups de banco

### `Procfile`
Simples comando de start para Heroku/Railway:
```
web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### `railway.json`
Config Railway com restart policy:
```json
{
  "build": {"builder": "NIXPACKS"},
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### `render.yaml`
Configuração completa Render:
- Runtime Python 3.11
- Build e start commands
- Variáveis de ambiente (algumas auto-geradas)
- Disco persistente de 1GB

### `fly.toml`
Config Fly.io com:
- Região primária: `gru` (São Paulo)
- Auto-scaling habilitado
- Volume montado em `/data`
- Healthcheck em `/health`

### `Dockerfile.production`
Multi-stage build otimizado:
- Base: `python:3.11-slim`
- Instala apenas dependências necessárias
- Copia código da aplicação
- Healthcheck configurado
- Porta 8000 exposta

---

## 🧪 Testes Antes de Deploy

### Validar Localmente

```bash
# 1. Configurar ambiente
$env:SECRET_KEY="test-key-123456789012345678901234"
$env:ENVIRONMENT="development"
$env:PORT="8000"

# 2. Testar import
python -c "from app.main import app; print('✓ OK')"

# 3. Rodar servidor
python start_server.py

# 4. Testar endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/health
```

### Rodar Testes

```bash
python run_tests.py
```

**Resultado esperado:** `57 passed`

---

## 📋 Checklist Pré-Deploy

- [ ] Git inicializado (`git init`)
- [ ] `.gitignore` configurado
- [ ] Código commitado no GitHub
- [ ] `.env.example` atualizado
- [ ] Testes passando localmente
- [ ] SECRET_KEY gerada para produção
- [ ] Plataforma cloud escolhida
- [ ] Documentação revisada

---

## 📊 Comparação de Plataformas

### Railway
**Prós:**
- ✅ Setup mais rápido (< 5 min)
- ✅ Interface intuitiva
- ✅ Deploy automático no push

**Contras:**
- ⚠️ Free tier limitado (500h/mês)
- ⚠️ Sleep após inatividade

### Render
**Prós:**
- ✅ Free tier permanente
- ✅ Disco persistente incluído
- ✅ SSL automático

**Contras:**
- ⚠️ Spin-down após 15min inatividade (free tier)
- ⚠️ Cold start lento (~30s)

### Fly.io
**Prós:**
- ✅ Performance excelente
- ✅ Múltiplas regiões
- ✅ CLI poderosa

**Contras:**
- ⚠️ Curva de aprendizado maior
- ⚠️ Requer cartão de crédito (não cobra)

---

## 🆘 Troubleshooting

### "Git not found"
```bash
# Instalar Git
# Windows: https://git-scm.com
# Linux: sudo apt install git
# Mac: brew install git
```

### "Authentication failed" (GitHub)
```bash
# Configurar credenciais
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"

# Usar token de acesso pessoal
# Settings → Developer settings → Personal access tokens
```

### "Application failed to start" (Deploy)
1. Verifique logs da plataforma
2. Confirme que `SECRET_KEY` está configurada
3. Valide que `requirements.txt` está completo
4. Teste localmente com `python start_server.py`

### "Module not found"
```bash
# Rebuild dependências
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Próximos Passos Após Deploy

1. **Configurar Domínio Customizado** (opcional)
   - Railway: Settings → Domains
   - Render: Settings → Custom Domains
   - Fly.io: `fly certs add seu-dominio.com`

2. **Configurar Backups Automáticos**
   - Ver `DEPLOY.md` seção "Backups"

3. **Monitoramento**
   - Configurar alertas de downtime
   - Integrar com Sentry (erros)
   - Configurar uptime monitoring (UptimeRobot, etc.)

4. **Migrar para PostgreSQL** (se necessário)
   - Railway: Add PostgreSQL plugin
   - Render: Add PostgreSQL database
   - Fly.io: `fly postgres create`

5. **Criar Ambiente de Staging**
   - Seguir instruções em `ENVIRONMENTS.md`

---

## 📞 Suporte

- 📖 Documentação completa: `DEPLOY.md`
- 🚀 Quick start: `QUICKSTART-DEPLOY.md`
- 🌍 Múltiplos ambientes: `ENVIRONMENTS.md`
- 🐛 Abrir issue no GitHub para problemas

---

**Boa sorte com o deploy! 🚀**
