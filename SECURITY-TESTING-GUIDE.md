# Guia de Teste - Melhorias de Segurança

## Como Validar as Melhorias

### 1. Iniciar o Servidor

```powershell
# No terminal PowerShell
$env:PORT="8010"
$env:SECRET_KEY="dev-secret-key-change-in-production"
& ".venv/Scripts/python.exe" start_server.py
```

Você deverá ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8010
```

---

## 2. Testar Content Security Policy (CSP)

### No Navegador:

1. Abra o Chrome/Edge em `http://localhost:8010`
2. Abra DevTools (`F12`)
3. Vá para a aba **Network**
4. Recarregue a página (`Ctrl+R`)
5. Clique em qualquer requisição (ex: `login` ou `/`)
6. Na aba **Headers**, procure por `Content-Security-Policy`

**Você deve ver algo como:**
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123xyz...'; style-src 'self' 'unsafe-inline'; ...
```

### Verificar Console:
- **NÃO** deve haver erros de CSP
- Scripts inline devem funcionar normalmente
- O nonce deve ser **diferente** a cada reload da página

---

## 3. Testar Isolamento Multi-Tenant

### Criar Dois Usuários:

#### Usuário 1:
```powershell
$body = @{
    email = "usuario1@teste.com"
    password = "Senha@123"
    nome = "Usuário Um"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8010/auth/register" -Method Post -ContentType "application/json" -Body $body
```

#### Usuário 2:
```powershell
$body = @{
    email = "usuario2@teste.com"
    password = "Senha@456"
    nome = "Usuário Dois"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8010/auth/register" -Method Post -ContentType "application/json" -Body $body
```

### Fazer Login como Usuário 1:
```powershell
$body = @{
    email = "usuario1@teste.com"
    password = "Senha@123"
} | ConvertTo-Json

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8010/auth/login" -Method Post -ContentType "application/json" -Body $body -SessionVariable session
```

### Criar Lançamento como Usuário 1:
```powershell
$body = @{
    data_lancamento = "2025-11-01"
    tipo = "despesa"
    tipo_lancamento_id = 1
    fornecedor = "Teste Privado Usuário 1"
    valor_total = 100.50
    data_primeiro_vencimento = "2025-11-10"
    numero_parcelas = 1
    valor_medio_parcelas = 100.50
} | ConvertTo-Json

$lancamento1 = Invoke-RestMethod -Uri "http://127.0.0.1:8010/api/lancamentos" -Method Post -ContentType "application/json" -Body $body -WebSession $session
Write-Host "Lançamento criado com ID: $($lancamento1.id)"
```

### Fazer Login como Usuário 2:
```powershell
$body = @{
    email = "usuario2@teste.com"
    password = "Senha@456"
} | ConvertTo-Json

$session2 = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8010/auth/login" -Method Post -ContentType "application/json" -Body $body -SessionVariable session2
```

### Tentar Acessar Lançamento do Usuário 1:
```powershell
# Use o ID do lançamento criado anteriormente
$idLancamento = $lancamento1.id

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8010/api/lancamentos/$idLancamento" -WebSession $session2
    Write-Host "❌ FALHA: Usuário 2 conseguiu acessar dados do Usuário 1!"
} catch {
    Write-Host "✅ SUCESSO: Acesso bloqueado corretamente! (404 esperado)"
    Write-Host "Erro: $($_.Exception.Message)"
}
```

**Resultado esperado:** `404 Not Found` - O isolamento está funcionando!

---

## 4. Testar Exportações Isoladas

### Como Usuário 1, criar mais lançamentos:
```powershell
# (repetir comando de criação de lançamento várias vezes com dados diferentes)
```

### Exportar Excel como Usuário 1:
```powershell
$excel1 = Invoke-WebRequest -Uri "http://127.0.0.1:8010/api/relatorios/lancamentos-excel" -WebSession $session -OutFile "usuario1.xlsx"
Write-Host "✅ Excel do Usuário 1 exportado"
```

### Exportar Excel como Usuário 2:
```powershell
$excel2 = Invoke-WebRequest -Uri "http://127.0.0.1:8010/api/relatorios/lancamentos-excel" -WebSession $session2 -OutFile "usuario2.xlsx"
Write-Host "✅ Excel do Usuário 2 exportado"
```

### Verificar:
- Abra os arquivos Excel
- `usuario1.xlsx` deve conter apenas lançamentos do Usuário 1
- `usuario2.xlsx` deve conter apenas lançamentos do Usuário 2 (ou estar vazio se não criou nenhum)

---

## 5. Testar Dashboard Isolado

### No Navegador:

1. Faça login como **Usuário 1**
2. Vá para o **Dashboard** (`/`)
3. Observe os valores totalizados
4. Faça logout
5. Faça login como **Usuário 2**
6. Vá para o **Dashboard** novamente

**Resultado esperado:**
- Dashboard do Usuário 2 deve mostrar valores **diferentes** ou **zerados**
- Dashboard do Usuário 1 deve mostrar apenas seus próprios dados

---

## 6. Testar Notificações Isoladas

### API via PowerShell:

```powershell
# Como Usuário 1
$notif1 = Invoke-RestMethod -Uri "http://127.0.0.1:8010/api/notificacoes" -WebSession $session
Write-Host "Notificações Usuário 1: $($notif1.total)"

# Como Usuário 2
$notif2 = Invoke-RestMethod -Uri "http://127.0.0.1:8010/api/notificacoes" -WebSession $session2
Write-Host "Notificações Usuário 2: $($notif2.total)"
```

**Resultado esperado:**
- Cada usuário vê apenas suas próprias notificações
- Totais devem ser diferentes

---

## 7. Verificar Headers de Segurança

```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8010/login"
$response.Headers
```

**Você deve ver:**
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-...'; ...
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## 8. Testar Rate Limiting

### Tentar fazer login múltiplas vezes com senha errada:

```powershell
for ($i = 1; $i -le 12; $i++) {
    $body = @{
        email = "usuario1@teste.com"
        password = "SenhaErrada$i"
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:8010/auth/login" -Method Post -ContentType "application/json" -Body $body
    } catch {
        Write-Host "Tentativa $i : $($_.Exception.Message)"
    }
    Start-Sleep -Milliseconds 100
}
```

**Resultado esperado:**
- Primeiras 10 tentativas: `401 Unauthorized` (credenciais inválidas)
- Tentativas 11 e 12: `429 Too Many Requests` (rate limit ativado)

Após 1 minuto, o rate limit reseta.

---

## 9. Executar Suite de Testes

```powershell
& ".venv/Scripts/python.exe" -m pytest tests/ -v
```

**Resultado esperado:**
```
57 passed, 13 warnings in ~30s
```

---

## 10. Checklist Final

- [ ] Servidor inicia sem erros
- [ ] CSP com nonce aparece nos headers
- [ ] Scripts inline funcionam (sem erros no console)
- [ ] Usuário 2 **NÃO** acessa dados do Usuário 1
- [ ] Exportações isoladas por usuário
- [ ] Dashboard mostra apenas dados do usuário logado
- [ ] Notificações isoladas
- [ ] Headers de segurança presentes
- [ ] Rate limiting funciona
- [ ] Todos os testes passam

---

## Problemas Comuns

### CSP bloqueando scripts
**Sintoma:** Console mostra `Refused to execute inline script`

**Solução:** Verificar que:
1. O nonce está sendo gerado no middleware
2. Templates usam `get_template_context(request)`
3. Tags `<script>` têm o atributo nonce condicional

### Usuário consegue acessar dados de outro
**Sintoma:** API retorna dados em vez de 404

**Solução:** Verificar que:
1. Endpoint usa `current_user: User = Depends(...)`
2. Query filtra por `usuario_id == current_user.id`
3. Registro pertence ao usuário antes de retornar

### Rate limit não funciona
**Sintoma:** Consegue fazer mais de 10 tentativas sem bloqueio

**Solução:** Verificar que:
1. Middleware está registrado
2. Path está em `SENSITIVE_RATE_PATHS`
3. Usando o mesmo IP/sessão

---

## Comandos Rápidos (Resumo)

```powershell
# Iniciar servidor
$env:PORT="8010"; $env:SECRET_KEY="dev-key"; & ".venv/Scripts/python.exe" start_server.py

# Rodar testes
& ".venv/Scripts/python.exe" -m pytest tests/ -v

# Verificar headers
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8010/login"
$response.Headers['Content-Security-Policy']

# Criar usuário
$body = '{"email":"teste@exemplo.com","password":"Senha@123","nome":"Teste"}' 
Invoke-RestMethod -Uri "http://127.0.0.1:8010/auth/register" -Method Post -ContentType "application/json" -Body $body
```

---

**Última atualização:** 07/11/2025  
**Versão:** 2.0 (Hardening Completo)
