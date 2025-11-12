# ✅ Checklist Rápido - Deploy no Render

Imprima ou deixe essa página aberta enquanto configura!

---

## 🎯 AMBIENTE DE PRODUÇÃO

### Passo 1: Criar Web Service
- [ ] Render.com → Login
- [ ] Botão "New +" → "Web Service"
- [ ] Conectar repositório: `sistema-financeiro-pessoal`

### Passo 2: Configuração Básica
```
Name:          financeiro-prod
Region:        Oregon (US West)
Branch:        main
Root Dir:      (vazio)
Runtime:       Python 3
```

### Passo 3: Comandos
```
Build Command:
pip install -r requirements.txt

Start Command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Passo 4: Plano
- [ ] Selecionar: **Free**

### Passo 5: Variáveis de Ambiente
- [ ] Adicionar 4 variáveis:

```
SECRET_KEY       WKH47dIysRZfVmVjtCMCQMnyi8juy4Xuy1LdUdTDTUk
ENVIRONMENT      production
LOG_LEVEL        info
DB_PATH          /opt/render/project/src/data/lancamentos.db
```

### Passo 6: Disco Persistente
- [ ] Add Disk:
```
Name:         data
Mount Path:   /opt/render/project/src/data
Size:         1 GB
```

### Passo 7: Deploy
- [ ] Clicar "Create Web Service"
- [ ] Aguardar build (2-5 min)
- [ ] Copiar URL: `https://financeiro-prod.onrender.com`

### Passo 8: Testar
- [ ] Abrir: `https://financeiro-prod.onrender.com/health`
- [ ] Ver: `{"status":"ok"}`
- [ ] Fazer login: `admin@sistema.com` / `admin123`
- [ ] Alterar senha padrão!

---

## 🧪 AMBIENTE DE TESTE (Opcional)

### Repetir Passos 1-7, mas com:

```
Name:          financeiro-teste
Branch:        main (ou develop se criou)
SECRET_KEY:    vKxL9ykkmLelSAsBhyq82ILIMWRvV2D7GmSF9e7cf5w
ENVIRONMENT:   staging
DB_PATH:       /opt/render/project/src/data/lancamentos_staging.db
Disk Name:     data-staging
```

---

## 📋 Valores para Copiar/Colar

### Build Command
```
pip install -r requirements.txt
```

### Start Command
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### SECRET_KEY Produção
```
WKH47dIysRZfVmVjtCMCQMnyi8juy4Xuy1LdUdTDTUk
```

### SECRET_KEY Teste
```
vKxL9ykkmLelSAsBhyq82ILIMWRvV2D7GmSF9e7cf5w
```

### DB_PATH Produção
```
/opt/render/project/src/data/lancamentos.db
```

### DB_PATH Teste
```
/opt/render/project/src/data/lancamentos_staging.db
```

### Mount Path
```
/opt/render/project/src/data
```

---

## 🆘 Em Caso de Erro

### "Application failed to start"
1. Ver Logs (menu lateral)
2. Verificar se SECRET_KEY está configurada
3. Verificar Start Command

### "No module named 'app'"
- Start Command está errado
- Deve ser: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Dados perdidos ao reiniciar
- Disco persistente não foi configurado
- Settings → Disks → Add Disk

---

## ✅ Depois do Deploy

- [ ] Configurar Health Check: Settings → Health Check Path → `/health`
- [ ] Testar todas as páginas principais
- [ ] Alterar senha do admin
- [ ] Adicionar domínio customizado (opcional)
- [ ] Configurar alertas de uptime (UptimeRobot)

---

**URLs Importantes:**
- Render Dashboard: https://dashboard.render.com
- Documentação: https://render.com/docs
- Guia visual completo: RENDER-GUIA-VISUAL.md

---

**Precisa de ajuda?** Veja o arquivo `RENDER-GUIA-VISUAL.md` com explicações detalhadas!
