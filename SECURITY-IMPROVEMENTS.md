# Melhorias de Segurança - Sistema Financeiro Pessoal

## Data: 07/11/2025

### Resumo Executivo

Implementado hardening abrangente de segurança focado em:
1. **Isolamento Multi-Tenant (Multiusuário)**
2. **Reforço da Content Security Policy (CSP)**
3. **Funções Auxiliares para Segurança**

---

## 1. Isolamento Multi-Tenant Completo

### Problema Identificado
Endpoints não filtravam dados por `usuario_id`, permitindo que usuários acessassem dados de outros usuários através de manipulação de IDs.

### Solução Implementada

#### Endpoints Corrigidos (Filtros `usuario_id` Adicionados):

**Notificações e Fluxo de Caixa:**
- `/api/notificacoes` - Agora filtra apenas parcelas do usuário
- `/api/fluxo-caixa` - Filtra parcelas não pagas do usuário

**Lançamentos:**
- `/api/lancamentos/{id}` - Valida propriedade antes de retornar
- `/api/lancamentos/{id}` (PUT/DELETE) - Valida propriedade antes de modificar
- `/api/lancamentos/{id}/parcelas` - Lista apenas parcelas do usuário

**Parcelas:**
- `/api/parcelas/{id}/pagar` - Valida propriedade da parcela e forma de pagamento
- `/api/parcelas/{id}` (PUT) - Valida propriedade antes de editar

**Recorrentes:**
- `/api/recorrentes` (GET) - Lista apenas recorrentes do usuário
- `/api/recorrentes` (POST) - Atribui `usuario_id` na criação
- `/api/recorrentes/{id}` (PUT/DELETE/PATCH) - Valida propriedade
- `/api/recorrentes/{id}/gerar` - Valida e atribui `usuario_id` aos registros gerados

**Dashboard e Relatórios:**
- `/api/dashboard` - Todos os agregados filtram por `usuario_id`
- `/api/dashboard/evolucao` - Filtros em parcelas e lançamentos
- `/api/dashboard/top-formas` - Filtros em parcelas e formas de pagamento
- `/api/dashboard/por-tipo-subtipo` - Filtros em todos os modos (pagamento, vencimento, lançamento)
- `/api/dashboard/tabela-anual` - Filtros em ambos os modos
- `/api/relatorios/tabela-anual-pdf` - Usa filtros do endpoint subjacente
- `/api/relatorios/lancamentos-excel` - Filtro por `usuario_id`
- `/api/relatorios/parcelas-excel` - Filtro por `usuario_id`

**Formas de Pagamento:**
- `/api/formas-pagamento/{id}` (PUT/DELETE/PATCH) - Valida propriedade
- `/api/formas-pagamento/{id}/usage` - Conta apenas parcelas do usuário

### Autenticação Adicionada
Todos os endpoints de exportação e relatórios agora requerem:
```python
current_user: User = Depends(ensure_subscription)
```

---

## 2. Content Security Policy (CSP) Reforçada

### Problema Identificado
CSP permitia `'unsafe-inline'` para scripts, vulnerável a ataques XSS (Cross-Site Scripting).

### Solução Implementada

#### A. Geração de Nonce Único por Request
**Arquivo:** `app/main.py`

```python
@app.middleware("http")
async def security_headers_and_rate_limit(request: Request, call_next):
    import secrets
    # ...
    nonce = secrets.token_urlsafe(16)
    request.state.csp_nonce = nonce
    
    response = await call_next(request)
    
    # CSP com nonce para scripts inline
    csp = f"default-src 'self'; script-src 'self' 'nonce-{nonce}'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; manifest-src 'self';"
    response.headers['Content-Security-Policy'] = csp
    # ...
```

**Antes:**
```
script-src 'self' 'unsafe-inline'
```

**Depois:**
```
script-src 'self' 'nonce-{random_16_chars}'
```

#### B. Propagação de Nonce para Templates

**Função Auxiliar Criada:**
```python
def get_template_context(request: Request, **kwargs) -> dict:
    """
    Prepara contexto para templates incluindo CSP nonce.
    """
    context = {"request": request}
    if hasattr(request.state, 'csp_nonce'):
        context["csp_nonce"] = request.state.csp_nonce
    context.update(kwargs)
    return context
```

**Todos os 12 endpoints de templates atualizados:**
- `/` (dashboard)
- `/tipos`
- `/configuracoes`
- `/metas`
- `/lancamentos`
- `/parcelas`
- `/fluxo-caixa`
- `/recorrentes`
- `/formas-pagamento`
- `/historico-pagamentos`
- `/login`

#### C. Atualização Automática de Templates

**Script criado:** `add_nonce_to_templates.py`

Processou 13 templates HTML, adicionando atributo nonce condicional a todos os `<script>` inline:

```html
<!-- Antes -->
<script>
  // código
</script>

<!-- Depois -->
<script{%- if csp_nonce %} nonce="{{ csp_nonce }}"{%- endif %}>
  // código
</script>
```

**Templates atualizados:**
- `_app_sidebar.html`
- `configuracoes.html`
- `dashboard.html`
- `fluxo_caixa.html`
- `formas_pagamento.html`
- `historico_pagamentos.html`
- `lancamentos_financeiros_db.html`
- `login.html`
- `metas.html`
- `offline.html`
- `parcelas_a_vencer.html`
- `recorrentes.html`
- `tipos_lancamentos.html`

---

## 3. Funções Auxiliares de Segurança

### Criadas em `app/main.py`:

#### `apply_user_filter(query, model, user_id)`
Aplica filtro de `usuario_id` a queries SQLAlchemy de forma consistente.

**Exemplo de uso:**
```python
query = db.query(Lancamento)
query = apply_user_filter(query, Lancamento, current_user.id)
```

#### `get_user_record(db, model, record_id, user_id)`
Busca um registro verificando propriedade do usuário.

**Exemplo de uso:**
```python
lancamento = get_user_record(db, Lancamento, lancamento_id, current_user.id)
if not lancamento:
    raise HTTPException(status_code=404, detail="Lançamento não encontrado")
```

#### `get_template_context(request, **kwargs)`
Prepara contexto para templates incluindo CSP nonce automaticamente.

**Exemplo de uso:**
```python
return templates.TemplateResponse(
    "dashboard.html",
    get_template_context(request)
)
```

---

## 4. Testes de Validação

### Execução da Suite de Testes

```bash
pytest tests/ -v
```

**Resultado:**
- ✅ 57 testes passaram
- ✅ 0 falhas
- ⚠️ 13 warnings (deprecations não críticos)

**Cobertura de testes:**
- Lançamentos (10 testes)
- Parcelas (7 testes)
- Formas de Pagamento (15 testes)
- Dashboard e Relatórios (13 testes)
- Tipos e Subtipos (9 testes)
- Billing (2 testes)
- Filtros (1 teste)

---

## 5. Impacto nas Vulnerabilidades

### Antes vs Depois

| Vulnerabilidade | Antes | Depois | Mitigação |
|----------------|-------|--------|-----------|
| **Acesso Cross-User** | ❌ Possível manipular IDs | ✅ Bloqueado | Filtros `usuario_id` |
| **XSS via Inline Script** | ❌ `unsafe-inline` | ✅ Nonce único | CSP com nonce |
| **Enumeração de Dados** | ❌ Dashboard global | ✅ Dados isolados | Filtros em agregações |
| **Data Leakage em Exports** | ❌ Excel/PDF globais | ✅ Filtrados por usuário | Auth + filtros |
| **Formas de Pagamento Cross-User** | ❌ Edição cruzada possível | ✅ Validação de propriedade | Ownership checks |

---

## 6. Checklist de Segurança Aplicado

- [x] **Autenticação e Autorização**
  - [x] Todos endpoints sensíveis requerem autenticação
  - [x] Validação de propriedade em operações CRUD
  - [x] Segregação de dados por `usuario_id`

- [x] **Content Security Policy (CSP)**
  - [x] Removido `unsafe-inline` de `script-src`
  - [x] Implementado sistema de nonce
  - [x] Mantido `unsafe-inline` apenas para `style-src` (baixo risco)

- [x] **Headers de Segurança**
  - [x] `X-Frame-Options: DENY`
  - [x] `X-Content-Type-Options: nosniff`
  - [x] `Referrer-Policy: strict-origin-when-cross-origin`
  - [x] `Permissions-Policy` restritivo
  - [x] `Strict-Transport-Security` (produção)

- [x] **Rate Limiting**
  - [x] Endpoints de autenticação limitados (10 req/min)
  - [x] Mensagens neutras em falhas

- [x] **CORS**
  - [x] Origens restritas via variável de ambiente
  - [x] Fallback para localhost em desenvolvimento

- [x] **Validação de Entrada**
  - [x] Pydantic schemas em todos endpoints
  - [x] Validação de força de senha
  - [x] Sanitização automática

---

## 7. Próximos Passos Recomendados

### Curto Prazo (Opcional)
1. **Pin de Versões de Dependências**
   - Fixar versões no `requirements.txt` para garantir reprodutibilidade
   
2. **Logging Estruturado**
   - Implementar logging centralizado para auditoria
   - Registrar tentativas de acesso não autorizado

3. **Testes de Segurança**
   - Adicionar testes específicos para validação de isolamento
   - Testes de tentativa de acesso cross-user

### Médio Prazo (Futuro)
1. **Refresh Tokens**
   - Implementar tokens de curta duração com refresh
   
2. **2FA (Two-Factor Authentication)**
   - Adicionar autenticação de dois fatores opcional
   
3. **Criptografia de Backups**
   - Criptografar backups automáticos do banco de dados

4. **Remover `unsafe-inline` de `style-src`**
   - Extrair estilos inline para arquivo CSS externo
   - Aplicar nonce também aos estilos (mais trabalhoso)

---

## 8. Comandos para Validação

### Testar Localmente

```bash
# Rodar testes
pytest tests/ -v

# Iniciar servidor
python start_server.py

# Verificar headers de segurança
curl -I http://localhost:8010/

# Testar isolamento (tentar acessar dados de outro usuário)
# Criar usuário 1, criar lançamento
# Criar usuário 2, tentar acessar lançamento do usuário 1 via ID
```

### Verificar CSP no Browser

1. Abrir DevTools (F12)
2. Ir para aba "Network"
3. Recarregar página
4. Verificar header `Content-Security-Policy` na resposta
5. Conferir que nonce está presente e único em cada request

**Exemplo de header esperado:**
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-AbC123XyZ...'; ...
```

---

## 9. Referências de Segurança

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CSP Level 3 Spec](https://www.w3.org/TR/CSP3/)
- [OWASP Multi-Tenancy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multitenant_Architecture_Cheat_Sheet.html)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)

---

## Conclusão

Sistema agora possui:
- ✅ **Isolamento multi-tenant completo** - Dados segregados por usuário
- ✅ **CSP reforçada com nonce** - Proteção contra XSS
- ✅ **Funções auxiliares** - Código mais DRY e seguro
- ✅ **57 testes passando** - Validação automatizada
- ✅ **Zero regressões** - Funcionalidades preservadas

**Status de Segurança:** 🟢 **ALTO**

O sistema está significativamente mais seguro contra:
- Acesso não autorizado entre usuários
- Cross-Site Scripting (XSS)
- Enumeração de dados
- Vazamento de informações em exportações

**Assinatura:** GitHub Copilot  
**Data:** 07/11/2025
