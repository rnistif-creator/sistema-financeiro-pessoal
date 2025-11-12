# 🎯 Guia Passo-a-Passo: Deploy no Render

Este guia mostra **exatamente** o que fazer no Render, passo por passo.

---

## 📋 Antes de Começar

Você já tem:
- ✅ Código no GitHub (https://github.com/rnistif-creator/sistema-financeiro-pessoal)
- ✅ Conta no Render vinculada ao GitHub

Agora vamos fazer o deploy!

---

## 🚀 Passo 1: Criar Novo Web Service

### 1.1 Acessar Dashboard do Render

1. Abra: https://render.com
2. Faça login
3. Você verá o **Dashboard** do Render

### 1.2 Criar Novo Serviço

1. Clique no botão **"New +"** (canto superior direito)
2. No menu que aparece, clique em **"Web Service"**

![Render Dashboard - Botão New]
```
┌─────────────────────────────────────┐
│ Render Dashboard         [New +] ▼  │
├─────────────────────────────────────┤
│                                     │
│  Clique aqui → [New +]              │
│                ↓                    │
│                Web Service          │
│                Background Worker    │
│                Cron Job             │
│                Static Site          │
└─────────────────────────────────────┘
```

---

## 🔗 Passo 2: Conectar Repositório

### 2.1 Selecionar Repositório

Você verá uma lista dos seus repositórios do GitHub.

1. Procure: **`sistema-financeiro-pessoal`**
2. Clique no botão **"Connect"** ao lado dele

```
┌──────────────────────────────────────────────────┐
│ Connect a repository                             │
├──────────────────────────────────────────────────┤
│ 🔍 Search repositories...                        │
│                                                  │
│ □ rnistif-creator/sistema-financeiro-pessoal    │
│   [Connect]  ← CLIQUE AQUI                       │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Se não aparecer o repositório:**
- Clique em "Configure GitHub App"
- Dê permissão ao Render para acessar o repositório

---

## ⚙️ Passo 3: Configurar o Serviço

Agora você verá um formulário grande. Vou explicar cada campo:

### 3.1 Informações Básicas

```
┌─────────────────────────────────────────────┐
│ Create Web Service                          │
├─────────────────────────────────────────────┤
│                                             │
│ Name *                                      │
│ ┌─────────────────────────────────────┐    │
│ │ financeiro-prod                     │    │
│ └─────────────────────────────────────┘    │
│ Digite: financeiro-prod                     │
│                                             │
│ Region                                      │
│ ┌─────────────────────────────────────┐    │
│ │ Oregon (US West) ▼                  │    │
│ └─────────────────────────────────────┘    │
│ Deixe Oregon (ou escolha outra)             │
│                                             │
│ Branch                                      │
│ ┌─────────────────────────────────────┐    │
│ │ main ▼                              │    │
│ └─────────────────────────────────────┘    │
│ Deixe: main                                 │
│                                             │
│ Root Directory                              │
│ ┌─────────────────────────────────────┐    │
│ │ (deixe vazio)                       │    │
│ └─────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

**Preencha:**
- **Name:** `financeiro-prod` (ou outro nome que preferir)
- **Region:** Oregon (US West) - pode deixar padrão
- **Branch:** `main` - deixe assim
- **Root Directory:** (deixe vazio)

### 3.2 Runtime e Comandos

Role para baixo, você verá:

```
┌─────────────────────────────────────────────┐
│ Runtime                                     │
│ ┌─────────────────────────────────────┐    │
│ │ Python 3 ▼                          │    │
│ └─────────────────────────────────────┘    │
│ Escolha: Python 3                           │
│                                             │
│ Build Command                               │
│ ┌─────────────────────────────────────┐    │
│ │ pip install -r requirements.txt     │    │
│ └─────────────────────────────────────┘    │
│ Cole isso (pode já estar preenchido)        │
│                                             │
│ Start Command                               │
│ ┌─────────────────────────────────────┐    │
│ │ uvicorn app.main:app --host 0.0.0.0 │    │
│ │ --port $PORT                        │    │
│ └─────────────────────────────────────┘    │
│ Cole isso                                   │
│                                             │
└─────────────────────────────────────────────┘
```

**Preencha:**

**Runtime:** 
- Selecione: `Python 3`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python pre_start.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Nota:** O `pre_start.py` garante que os diretórios necessários existem antes de iniciar.

### 3.3 Plano (Free Tier)

```
┌─────────────────────────────────────────────┐
│ Instance Type                               │
│                                             │
│ ○ Free                                      │
│   512 MB RAM • Sleeps after 15 min          │
│                                             │
│ ○ Starter ($7/mo)                           │
│   512 MB RAM • Always on                    │
│                                             │
└─────────────────────────────────────────────┘
```

**Escolha:**
- Marque: **Free** (para começar)

---

## 🔐 Passo 4: Variáveis de Ambiente (IMPORTANTE!)

Role até a seção **"Environment Variables"**

### 4.1 Gerar SECRET_KEY

**No seu terminal local, rode:**

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Vai aparecer algo como: `xK3mP9qR7vN2wL8dF5bH1jT6gY4cZ0uA`

**COPIE ESSE VALOR!**

### 4.2 Adicionar Variáveis

No formulário do Render:

```
┌─────────────────────────────────────────────┐
│ Environment Variables                       │
│                                             │
│ [Add Environment Variable]                  │
│                                             │
│ Key             Value                       │
│ ┌─────────┐    ┌───────────────────────┐   │
│ │         │    │                       │   │
│ └─────────┘    └───────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

**Clique em "Add Environment Variable"** e adicione cada uma dessas (clique 4 vezes):

**Variável 1:**
- **Key:** `SECRET_KEY`
- **Value:** (cole o valor que você gerou acima)

**Variável 2:**
- **Key:** `ENVIRONMENT`
- **Value:** `production`

**Variável 3:**
- **Key:** `LOG_LEVEL`
- **Value:** `info`

**Variável 4:**
- **Key:** `DB_PATH`
- **Value:** `/opt/render/project/src/data/lancamentos.db`

**Resultado final:**
```
┌─────────────────────────────────────────────────────┐
│ Environment Variables                               │
├─────────────────────────────────────────────────────┤
│ SECRET_KEY       xK3mP9qR7vN2wL8dF5bH1jT6gY4cZ0uA   │
│ ENVIRONMENT      production                         │
│ LOG_LEVEL        info                               │
│ DB_PATH          /opt/render/project/src/data/...   │
└─────────────────────────────────────────────────────┘
```

---

## 💾 Passo 5: Disco Persistente (MUITO IMPORTANTE!)

**Sem isso, seus dados serão perdidos quando o servidor reiniciar!**

### 5.1 Encontrar a Seção

Role até encontrar **"Disk"** ou **"Persistent Disks"**

```
┌─────────────────────────────────────────────┐
│ Disks                                       │
│                                             │
│ [Add Disk]  ← CLIQUE AQUI                   │
│                                             │
└─────────────────────────────────────────────┘
```

### 5.2 Adicionar Disco

Clique em **"Add Disk"**. Um formulário aparece:

```
┌─────────────────────────────────────────────┐
│ Add Disk                                    │
├─────────────────────────────────────────────┤
│ Name                                        │
│ ┌─────────────────────────────────────┐    │
│ │ data                                │    │
│ └─────────────────────────────────────┘    │
│                                             │
│ Mount Path                                  │
│ ┌─────────────────────────────────────┐    │
│ │ /opt/render/project/src/data        │    │
│ └─────────────────────────────────────┘    │
│                                             │
│ Size                                        │
│ ┌─────────────────────────────────────┐    │
│ │ 1 GB (Free)                         │    │
│ └─────────────────────────────────────┘    │
│                                             │
│              [Add Disk]                     │
└─────────────────────────────────────────────┘
```

**Preencha:**
- **Name:** `data`
- **Mount Path:** `/opt/render/project/src/data`
- **Size:** `1 GB` (free tier)

Clique em **"Add Disk"**

---

## 🎯 Passo 6: Criar o Serviço

Agora role até o final da página.

Você verá um botão grande:

```
┌─────────────────────────────────────────────┐
│                                             │
│         [Create Web Service]                │
│                                             │
└─────────────────────────────────────────────┘
```

**Clique em "Create Web Service"**

---

## ⏳ Passo 7: Aguardar o Deploy

### 7.1 Acompanhar o Build

O Render vai:
1. Baixar seu código do GitHub
2. Instalar as dependências (`pip install`)
3. Iniciar o servidor

Você verá logs em tempo real:

```
┌─────────────────────────────────────────────┐
│ Logs                                        │
├─────────────────────────────────────────────┤
│ ==> Cloning from GitHub...                 │
│ ==> Installing dependencies...             │
│ Collecting fastapi>=0.108.0                │
│ Installing collected packages...           │
│ ==> Starting service...                    │
│ INFO: Started server process               │
│ INFO: Application startup complete         │
│ ==> Build successful!                      │
│ ==> Your service is live 🎉                │
└─────────────────────────────────────────────┘
```

**Aguarde até ver:** `Your service is live` (demora 2-5 minutos)

### 7.2 URL da Aplicação

No topo da página, você verá a URL:

```
┌─────────────────────────────────────────────┐
│ financeiro-prod                             │
│ https://financeiro-prod.onrender.com        │
│ [Open]  ← CLIQUE PARA TESTAR                │
└─────────────────────────────────────────────┘
```

---

## ✅ Passo 8: Testar a Aplicação

### 8.1 Testar Health Check

Abra no navegador:
```
https://seu-servico.onrender.com/health
```

**Deve aparecer:**
```json
{"status":"ok","database":"connected"}
```

### 8.2 Acessar o Sistema

Abra:
```
https://seu-servico.onrender.com
```

**Fazer login:**
- **Email:** `admin@sistema.com`
- **Senha:** `admin123`

**⚠️ IMPORTANTE:** Após o primeiro login, vá em Configurações e altere a senha!

---

## 🎉 Pronto! Aplicação no Ar!

Sua aplicação está rodando em produção no Render!

---

## 🔧 Configurações Adicionais (Opcional)

### Health Check Path

Depois do deploy, configure o health check:

1. Vá em **Settings** (no menu lateral)
2. Role até **Health Check Path**
3. Digite: `/health`
4. Salve

```
┌─────────────────────────────────────────────┐
│ Health Check                                │
│                                             │
│ Health Check Path                           │
│ ┌─────────────────────────────────────┐    │
│ │ /health                             │    │
│ └─────────────────────────────────────┘    │
│                                             │
│ [Save Changes]                              │
└─────────────────────────────────────────────┘
```

### Auto-Deploy (já está ativo)

Qualquer push para o GitHub faz deploy automático!

```bash
# No seu computador
git add .
git commit -m "Nova funcionalidade"
git push origin main

# Render detecta e faz deploy automaticamente!
```

---

## 📊 Resumo das Configurações

| Item | Valor |
|------|-------|
| **Name** | `financeiro-prod` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Branch** | `main` |
| **Instance Type** | Free |
| **SECRET_KEY** | (gerado com python) |
| **ENVIRONMENT** | `production` |
| **LOG_LEVEL** | `info` |
| **DB_PATH** | `/opt/render/project/src/data/lancamentos.db` |
| **Disk Name** | `data` |
| **Disk Mount** | `/opt/render/project/src/data` |
| **Disk Size** | 1 GB |

---

## 🆘 Problemas Comuns

### Erro: "Application failed to start"

**Verifique:**
1. Logs no Render (menu lateral: **Logs**)
2. Se `SECRET_KEY` está configurada
3. Se o Start Command está correto

### Erro: "Database locked" ou dados perdidos

**Causa:** Disco persistente não configurado

**Solução:**
1. Settings → Disks
2. Add Disk (conforme Passo 5)

### Aplicação "dorme" após 15 min

**Isso é normal no Free Tier!** O primeiro acesso após dormir demora ~30s.

**Soluções:**
- Upgrade para Starter ($7/mês) - sempre ativo
- Usar serviço de "ping" (UptimeRobot) para manter acordado

---

## 🌍 Criar Ambiente de Teste (Staging)

Quer um ambiente separado para testes?

### Opção 1: Mesmo repositório, branch diferente

```bash
# Criar branch develop
git checkout -b develop
git push origin develop
```

Depois, repita os passos acima, mas:
- **Name:** `financeiro-staging`
- **Branch:** `develop`
- **SECRET_KEY:** (gerar uma NOVA, diferente)
- **DB_PATH:** `/opt/render/project/src/data/lancamentos_staging.db`
- **Disk Name:** `data-staging`

### Opção 2: Mesmo repositório, mesma branch

Repita os passos, mas use:
- **Name:** `financeiro-teste`
- **ENVIRONMENT:** `staging`
- **SECRET_KEY:** (diferente!)
- Disco separado

---

## 📚 Documentação Render

- [Render Docs](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-fastapi)
- [Persistent Disks](https://render.com/docs/disks)

---

**Dúvidas?** Pergunte que eu ajudo! 🚀
