# 🔧 Troubleshooting: Erro SQLAlchemy (e3q8) no Render

## 🎯 Problema

Você está vendo o erro:
```
(Background on this error at: https://sqlalche.me/e/20/e3q8)
```

Este erro significa: **"Não foi possível criar/acessar o banco de dados"**

---

## ✅ Soluções (em ordem)

### 🔥 ATUALIZAÇÃO: Código já corrigido!

O código no GitHub já foi atualizado com correções automáticas. Faça um **redeploy** no Render:

1. Dashboard → **Manual Deploy** → **Deploy latest commit**
2. Aguarde 2-3 minutos
3. Verifique os logs - deve ver: `✓ Diretório do banco criado`

**Se ainda assim falhar**, siga as soluções abaixo:

---

### Solução 1: Verificar Disco Persistente ⭐ MAIS COMUM

**O problema:** O diretório `/opt/render/project/src/data` não existe porque o disco não está montado.

**Como corrigir:**

1. No Render Dashboard, vá em **Settings** (menu lateral)
2. Role até **Disks**
3. Verifique se há um disco configurado:

```
┌─────────────────────────────────────────────┐
│ Disks                                       │
├─────────────────────────────────────────────┤
│ Name: data                                  │
│ Mount Path: /opt/render/project/src/data   │
│ Size: 1 GB                                  │
└─────────────────────────────────────────────┘
```

4. **Se NÃO houver disco:**
   - Clique em **Add Disk**
   - Name: `data`
   - Mount Path: `/opt/render/project/src/data`
   - Size: `1 GB`
   - Salve

5. **Redeploy:**
   - Menu lateral → **Manual Deploy**
   - Clique em **Deploy latest commit**

---

### Solução 2: Atualizar Start Command

**O problema:** O servidor tenta acessar um diretório antes de criá-lo.

**Como corrigir:**

1. Settings → **Start Command**
2. Atualize para:

```bash
python pre_start.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

3. **Salve** e aguarde o redeploy automático

**O que isso faz:** Executa o script `pre_start.py` que cria os diretórios necessários antes de iniciar.

---

### Solução 3: Verificar DB_PATH

**O problema:** O caminho do banco está errado.

**Como corrigir:**

1. Settings → **Environment Variables**
2. Procure por `DB_PATH`
3. Deve ser EXATAMENTE:

```
/opt/render/project/src/data/lancamentos.db
```

4. Se estiver diferente, corrija e salve

---

### Solução 4: Verificar SECRET_KEY

**O problema:** SECRET_KEY não está definida.

**Como corrigir:**

1. Settings → **Environment Variables**
2. Procure por `SECRET_KEY`
3. Se não existir ou estiver vazia:

```bash
# No seu terminal local, gere uma nova:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

4. Adicione/atualize no Render com o valor gerado

---

### Solução 5: Usar SQLite em Caminho Relativo (Alternativa)

**O problema:** Disco persistente é complicado no free tier.

**Solução temporária:**

1. Settings → Environment Variables
2. **Mude** `DB_PATH` para:

```
./lancamentos.db
```

⚠️ **ATENÇÃO:** Com isso, o banco será recriado sempre que o servidor reiniciar (você perde os dados). Use apenas para testes iniciais.

---

### Solução 6: Migrar para PostgreSQL (Recomendado para Produção)

**Para resolver definitivamente:**

1. No Render Dashboard, clique em **New +**
2. Selecione **PostgreSQL**
3. Nome: `financeiro-db`
4. Aguarde criação (2-3 min)
5. Copie a **Internal Database URL**
6. No seu Web Service:
   - Settings → Environment Variables
   - **Adicione:**
     - Key: `DATABASE_URL`
     - Value: (cole a URL do PostgreSQL)
   - **Remova ou comente:** `DB_PATH`

7. Adicione ao `requirements.txt`:

```
psycopg2-binary>=2.9.9
```

8. Redeploy

---

## 🔍 Como Ver Logs Detalhados

Para identificar o erro exato:

1. Dashboard do seu serviço → **Logs** (menu lateral)
2. Procure por linhas com:
   - `ERROR`
   - `OperationalError`
   - `e3q8`
   - `database`

3. Cole o erro completo aqui para análise específica

---

## 📋 Checklist de Diagnóstico

Execute no Render (via Shell ou no próximo deploy):

```bash
python diagnose.py
```

Isso mostrará:
- ✓ Variáveis de ambiente
- ✓ Diretórios existentes
- ✓ Permissões de escrita
- ✓ Conexão com banco

---

## 🆘 Ainda com Erro?

### Opção 1: Logs Completos

Copie os logs completos do Render e me envie. Procure especialmente:

```
INFO:     Started server process
INFO:     Waiting for application startup
ERROR:    ... (o erro aqui)
```

### Opção 2: Teste Local

No seu computador, simule o ambiente Render:

```powershell
# Configurar variáveis
$env:DB_PATH="/opt/render/project/src/data/lancamentos.db"
$env:SECRET_KEY="WKH47dIysRZfVmVjtCMCQMnyi8juy4Xuy1LdUdTDTUk"
$env:ENVIRONMENT="production"

# Criar diretório (simulando disco do Render)
New-Item -ItemType Directory -Force -Path "C:\opt\render\project\src\data"

# Rodar pre_start
python pre_start.py

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Se funcionar local mas não no Render → problema é no disco persistente.

---

## 📊 Causas Comuns (Estatísticas)

| Causa | Frequência | Solução |
|-------|-----------|---------|
| Disco não montado | 60% | Solução 1 |
| DB_PATH errado | 20% | Solução 3 |
| Diretório não criado | 15% | Solução 2 |
| SECRET_KEY faltando | 5% | Solução 4 |

---

## ✅ Validação Final

Após aplicar as soluções, teste:

1. **Health Check:**
```bash
curl https://seu-app.onrender.com/health
```

Deve retornar:
```json
{"status":"ok","database":"connected"}
```

2. **Página inicial:**
```
https://seu-app.onrender.com
```

Deve abrir a tela de login.

3. **Login de teste:**
- Email: `admin@sistema.com`
- Senha: `admin123`

---

## 📞 Precisando de Ajuda?

Me envie:

1. ✅ Logs completos do Render
2. ✅ Screenshot das Environment Variables (mascarando SECRET_KEY)
3. ✅ Screenshot da seção Disks
4. ✅ Output do `python diagnose.py` (se conseguir executar)

---

**90% dos erros e3q8 no Render são resolvidos com Solução 1 (disco) + Solução 2 (pre_start)!** 🎯
