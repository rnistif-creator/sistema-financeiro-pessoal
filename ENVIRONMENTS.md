# 🌍 Ambientes - Desenvolvimento vs Produção

Este guia explica como gerenciar múltiplos ambientes da aplicação.

---

## 🌐 URLs dos Ambientes

### Staging (Desenvolvimento/Testes)
- **URL:** https://sistema-financeiro-pessoal-staging.onrender.com
- **Branch:** `staging`
- **Auto-Deploy:** ✅ Ativado
- **Health Check:** https://sistema-financeiro-pessoal-staging.onrender.com/health
- **Status:** ✅ OPERACIONAL (última validação: 2025-11-12)

### Produção
- **URL:** [Configurar após setup]
- **Branch:** `main`
- **Auto-Deploy:** ❌ Desativado (deploy manual)
- **Health Check:** [URL]/health

---

## 📋 Ambientes Disponíveis

### 1. Desenvolvimento (Local)
- **Propósito:** Desenvolvimento e testes locais
- **Banco:** SQLite local (`lancamentos.db`)
- **Debug:** Habilitado
- **Hot Reload:** Sim

### 2. Teste/Staging (Cloud)
- **Propósito:** Testes antes de produção
- **Banco:** SQLite ou PostgreSQL
- **Debug:** Limitado
- **Dados:** Isolados da produção

### 3. Produção (Cloud)
- **Propósito:** Usuários reais
- **Banco:** PostgreSQL recomendado
- **Debug:** Desabilitado
- **Logs:** Estruturados

---

## 🔧 Configuração por Ambiente

### Desenvolvimento Local

**.env:**
```bash
ENVIRONMENT=development
SECRET_KEY=dev-secret-key-change-me
DB_PATH=lancamentos_dev.db
PORT=8000
LOG_LEVEL=debug
HOST=0.0.0.0
```

**Rodar:**
```bash
python start_server.py
# ou com reload
uvicorn app.main:app --reload
```

### Ambiente de Teste (Staging)

**Railway (Exemplo):**

1. **Criar novo projeto no Railway:**
   - Nome: `financeiro-staging`
   - Branch: `develop` (crie se não existir)

2. **Variáveis de ambiente:**
   ```
   ENVIRONMENT=staging
   SECRET_KEY=<gerar-nova-key>
   DB_PATH=/app/data/lancamentos_staging.db
   LOG_LEVEL=info
   ```

3. **Deploy automático:**
   - Push para `develop` → Deploy em staging
   - Push para `main` → Deploy em produção

### Produção

**Railway/Render/Fly.io:**

**Variáveis:**
```
ENVIRONMENT=production
SECRET_KEY=<key-super-secreta-aleatoria>
DB_PATH=/app/data/lancamentos.db
LOG_LEVEL=warning
PORT=8000
```

**Extras (recomendado):**
- Use PostgreSQL para melhor performance
- Configure backups automáticos
- Habilite monitoramento

---

## 🌿 Estratégia de Branches

### Gitflow Simplificado

```
main (produção)
  └── develop (staging)
       └── feature/nome-feature (desenvolvimento)
```

**Workflow:**

1. **Nova feature:**
   ```bash
   git checkout develop
   git checkout -b feature/nova-funcionalidade
   # ... desenvolver ...
   git add .
   git commit -m "feat: adiciona nova funcionalidade"
   git push origin feature/nova-funcionalidade
   ```

2. **Merge em staging:**
   ```bash
   # Via Pull Request ou:
   git checkout develop
   git merge feature/nova-funcionalidade
   git push origin develop
   # → Deploy automático em STAGING
   ```

3. **Promover para produção:**
   ```bash
   # Depois de testar em staging:
   git checkout main
   git merge develop
   git push origin main
   # → Deploy automático em PRODUÇÃO
   ```

---

## 🚀 Setup Múltiplos Ambientes

### Railway - Dois Ambientes

**1. Produção (main):**
```bash
# Já configurado pelo setup-git.ps1
```

**2. Staging (develop):**

```bash
# Criar branch develop
git checkout -b develop
git push origin develop

# No Railway:
# 1. Project Settings → Environments
# 2. "New Environment" → Nome: "staging"
# 3. Deployment Triggers → Branch: "develop"
# 4. Configure variáveis diferentes (SECRET_KEY, DB_PATH)
```

### Render - Múltiplos Services

**render.yaml (atualizado):**

```yaml
services:
  # Produção
  - type: web
    name: financeiro-prod
    runtime: python
    branch: main
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: SECRET_KEY
        generateValue: true

  # Staging
  - type: web
    name: financeiro-staging
    runtime: python
    branch: develop
    envVars:
      - key: ENVIRONMENT
        value: staging
      - key: SECRET_KEY
        generateValue: true
```

### Fly.io - Múltiplos Apps

```bash
# Produção
fly launch --name financeiro-prod --region gru
fly deploy

# Staging
fly launch --name financeiro-staging --region gru
fly deploy
```

---

## 🔐 Segurança entre Ambientes

### Isolamento de Dados

**✅ Fazer:**
- SECRET_KEY diferente em cada ambiente
- Bancos de dados completamente separados
- Credenciais únicas por ambiente
- Backups separados

**❌ Não fazer:**
- Usar mesma SECRET_KEY em staging e produção
- Compartilhar banco de dados
- Testar em produção

### Secrets Management

**Desenvolvimento:**
- `.env` local (gitignored)

**Staging/Produção:**
- Variáveis de ambiente na plataforma
- Nunca commitar secrets no Git
- Rotate keys periodicamente

---

## 📊 Monitoramento por Ambiente

### Desenvolvimento
- Logs no console
- Debug mode habilitado
- Sem preocupação com performance

### Staging
- Logs estruturados
- Simular condições de produção
- Testes de carga

### Produção
- Logs centralizados
- Alertas configurados
- Métricas de uptime
- Backup automático

---

## 🧪 Testes por Ambiente

### Local (Development)
```bash
# Rodar todos os testes
pytest -v

# Com coverage
pytest --cov=app tests/

# Testes específicos
pytest tests/test_dashboard.py
```

### Staging (Pre-Prod)
```bash
# Smoke tests
curl https://financeiro-staging.railway.app/health

# Testes de integração
pytest tests/integration/ --env=staging
```

### Produção
- Somente monitoramento
- Health checks automáticos
- Não rodar testes destrutivos

---

## 🔄 Migração de Dados entre Ambientes

### De Staging para Produção (Cuidado!)

**1. Backup de produção:**
```bash
# Sempre fazer backup antes!
python -c "from app.main import criar_backup; print(criar_backup())"
```

**2. Exportar de staging:**
```bash
python -c "from app.main import exportar_dados_json; print(exportar_dados_json(db))"
```

**3. Importar em produção:**
```bash
# Apenas se absolutamente necessário e testado
python import_data.py --from staging_export.json
```

**⚠️ Aviso:** Migração de dados entre ambientes é perigosa. Sempre teste localmente primeiro.

---

## 📝 Checklist de Deploy por Ambiente

### Staging
- [ ] Branch `develop` criado
- [ ] Deploy configurado no Railway/Render
- [ ] Variáveis de ambiente diferentes de produção
- [ ] Banco de dados separado
- [ ] SECRET_KEY única
- [ ] Testes automatizados passando

### Produção
- [ ] Branch `main` protegida (require PR)
- [ ] Variáveis de ambiente configuradas
- [ ] PostgreSQL configurado (recomendado)
- [ ] Backups automáticos habilitados
- [ ] Monitoramento ativo
- [ ] Domínio customizado (opcional)
- [ ] SSL/HTTPS habilitado

---

## 🆘 Rollback

### Railway/Render
- Dashboard → Deployments → Clique em deploy anterior → "Redeploy"

### Fly.io
```bash
fly releases
fly releases rollback <version>
```

### Git
```bash
# Reverter último commit
git revert HEAD
git push origin main
```

---

## 📚 Recursos

- [Railway Environments](https://docs.railway.app/deploy/environments)
- [Render Branch Deploys](https://render.com/docs/branch-deploys)
- [Fly.io Multiple Environments](https://fly.io/docs/app-guides/multiple-environments/)

---

**Pronto!** Agora você tem ambientes separados para desenvolvimento, teste e produção. 🎯
