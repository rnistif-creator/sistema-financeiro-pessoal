# 🚀 Configuração do Ambiente de Staging - Passo a Passo

## ✅ O que já foi feito automaticamente

- ✅ Branch `staging` criada e enviada para o GitHub
- ✅ Arquivo `render.yaml` atualizado com configuração de staging
- ✅ Health check configurado em ambos os ambientes
- ✅ CI/CD configurado no GitHub Actions
- ✅ Todos os testes passando (57/57)

---

## 📋 O QUE VOCÊ PRECISA FAZER NO RENDER (15 minutos)

### **PARTE 1: Criar o Serviço de Staging**

1. **Acesse o Render Dashboard**
   - Vá para: https://dashboard.render.com/

2. **Criar Novo Web Service**
   - Clique em **"New +"** (canto superior direito)
   - Selecione **"Web Service"**

3. **Conectar o Repositório**
   - Selecione o repositório: **`sistema-financeiro-pessoal`**
   - Clique em **"Connect"**

4. **Configurações Básicas**
   ```
   Name: sistema-financeiro-pessoal-staging
   Region: Oregon (US West)
   Branch: staging  ⚠️ IMPORTANTE: Mude de 'main' para 'staging'
   Runtime: Python 3
   ```

5. **Build & Deploy Settings**
   ```
   Build Command:
   pip install -r requirements.txt
   
   Start Command:
   python pre_start.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

6. **Environment Variables** (clique em "Add Environment Variable" para cada uma)
   ```
   PYTHON_VERSION = 3.11.0
   ENVIRONMENT = staging
   DB_PATH = /opt/render/project/src/data/lancamentos_staging.db
   LOG_LEVEL = debug
   SECRET_KEY = (deixe em branco - o Render vai gerar automaticamente)
   ```

7. **Plan**
   - Selecione: **Free** (o plano gratuito)

8. **Advanced Settings** (expanda a seção)
   - **Health Check Path**: `/health` ⚠️ IMPORTANTE
   - **Auto-Deploy**: ✅ Yes (deixe marcado)

9. **Adicionar Disco Persistente**
   - Role até a seção **"Disks"**
   - Clique em **"Add Disk"**
   ```
   Name: data
   Mount Path: /opt/render/project/src/data
   Size: 1 GB
   ```

10. **Criar o Serviço**
    - Clique no botão **"Create Web Service"**
    - ⏳ Aguarde 3-5 minutos enquanto o Render faz o primeiro deploy

11. **Copiar a URL do Staging**
    - Após o deploy, você verá algo como: `https://sistema-financeiro-pessoal-staging.onrender.com`
    - 📋 **COPIE ESTA URL** - você vai precisar dela!

---

### **PARTE 2: Configurar Health Check na Produção**

1. **Acesse o Serviço de Produção**
   - No Render Dashboard, clique no serviço: **`sistema-financeiro-pessoal`** (produção)

2. **Ir para Settings**
   - No menu lateral, clique em **"Settings"**

3. **Configurar Health Check**
   - Role até a seção **"Health & Alerts"**
   - Em **"Health Check Path"**, digite: `/health`
   - Clique em **"Save Changes"**

4. **Desativar Auto-Deploy (Produção)**
   - Na seção **"Build & Deploy"**
   - Desmarque a opção **"Auto-Deploy"** (produção deve ser manual)
   - Clique em **"Save Changes"**

5. **Verificar o Disco Persistente**
   - Role até a seção **"Disks"**
   - Confirme que existe um disco com:
     ```
     Name: data
     Mount Path: /opt/render/project/src/data
     Size: 1 GB
     ```
   - Se não existir, adicione conforme instruções da Parte 1, item 9

---

### **PARTE 3: Validar os Ambientes**

#### **Staging:**
1. Acesse: `https://sistema-financeiro-pessoal-staging.onrender.com/health`
   - ✅ Deve retornar: `{"status":"ok"}`

2. Acesse: `https://sistema-financeiro-pessoal-staging.onrender.com/login`
   - ✅ Deve mostrar a tela de login

3. Faça login e acesse o Dashboard
   - ✅ Deve funcionar normalmente

#### **Produção:**
1. Acesse: `https://seu-app-producao.onrender.com/health`
   - ✅ Deve retornar: `{"status":"ok"}`

2. Verifique se o app está funcionando normalmente

---

## 🤖 O QUE EU (COPILOT) VOU FAZER DEPOIS

Quando você me enviar a **URL do staging**, eu vou:

1. ✅ **Validar remotamente** que o health check está respondendo
2. ✅ **Atualizar documentação** com as URLs dos ambientes
3. ✅ **Criar script de smoke test** para validar ambos os ambientes
4. ✅ **Configurar alertas básicos** (opcional - se você quiser)

---

## 📊 FLUXO DE TRABALHO APÓS SETUP

### **Desenvolvimento Normal:**
```
1. Faça alterações no código localmente
2. Commit e push para a branch 'staging'
   → Render faz deploy AUTOMÁTICO no staging
3. Teste no staging
4. Se OK, abra um Pull Request: staging → main
5. Após merge, faça deploy MANUAL na produção
```

### **Deploy em Produção (Manual):**
```
1. Acesse o Render Dashboard
2. Selecione o serviço de produção
3. Clique em "Manual Deploy" → "Deploy latest commit"
4. Aguarde 2-3 minutos
5. Valide: /health e funcionalidades principais
```

---

## ❓ PRECISA DE AJUDA?

**Se algo der errado:**
1. Me envie a mensagem de erro que aparece no Render
2. Me envie os logs (no Render: "Logs" no menu lateral)
3. Eu vou diagnosticar e corrigir

**Próximos passos após configurar:**
- [ ] Backfill de tipos para lançamentos sem tipo
- [ ] Corrigir botões de filtro do Fluxo de Caixa
- [ ] Validar visualização do Dashboard

---

## 🎯 CHECKLIST RÁPIDO

**No Render - Staging:**
- [ ] Serviço criado com nome `sistema-financeiro-pessoal-staging`
- [ ] Branch: `staging`
- [ ] Health Check Path: `/health`
- [ ] Auto-Deploy: ✅ Ativado
- [ ] Disco: `data` montado em `/opt/render/project/src/data`
- [ ] Env vars: ENVIRONMENT=staging, DB_PATH com `_staging.db`
- [ ] Deploy completado com sucesso
- [ ] `/health` retorna `{"status":"ok"}`

**No Render - Produção:**
- [ ] Health Check Path: `/health` configurado
- [ ] Auto-Deploy: ❌ Desativado
- [ ] Disco: `data` confirmado e montado corretamente
- [ ] `/health` retorna `{"status":"ok"}`

---

## 📞 ME AVISE QUANDO:

1. ✅ Staging estiver no ar (me envie a URL)
2. ✅ Health check configurado na produção
3. ❌ Se encontrar qualquer erro ou dúvida

**Tempo estimado total: 10-15 minutos** ⏱️
