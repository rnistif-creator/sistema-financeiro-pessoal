# Testes Automatizados - Sistema Financeiro Pessoal

## ✅ Resumo da Execução

**Total: 34 testes - 100% de sucesso**

```
tests/test_dashboard.py ............ [12 testes]
tests/test_lancamentos.py ........... [10 testes]
tests/test_parcelas.py ........... [8 testes]
tests/test_tipos_lancamentos.py ..... [4 testes]
```

## 📊 Cobertura de Testes

### 1. Dashboard e Relatórios (12 testes)
- ✅ Totalizadores por período
- ✅ Filtro por tipo de lançamento
- ✅ Filtro por natureza (receita/despesa)
- ✅ Totalizador por data de vencimento
- ✅ Totalizador por data de pagamento
- ✅ Tabela anual de tipos
- ✅ Evolução mensal
- ✅ Exportação PDF da tabela anual
- ✅ Exportação Excel de lançamentos
- ✅ Exportação Excel de parcelas
- ✅ Dashboard sem dados
- ✅ Exportação sem dados

### 2. Lançamentos Financeiros (10 testes)
- ✅ Criar lançamento simples
- ✅ Listar lançamentos
- ✅ Obter lançamento por ID
- ✅ Obter lançamento com parcelas
- ✅ Atualizar lançamento
- ✅ Deletar lançamento
- ✅ Validação de dados obrigatórios
- ✅ Criar lançamento parcelado
- ✅ Filtrar por tipo (receita/despesa)
- ✅ Filtrar por período

### 3. Parcelas (8 testes)
- ✅ Listar parcelas a vencer
- ✅ Marcar parcela como paga
- ✅ Editar dados da parcela
- ✅ Filtrar por status (pagas/pendentes)
- ✅ Filtrar por tipo
- ✅ Pagar sem informar data (usa hoje)
- ✅ Estatísticas de parcelas

### 4. Tipos de Lançamento (4 testes)
- ✅ Criar tipo de lançamento
- ✅ Listar tipos
- ✅ Deletar tipo
- ✅ Validações (nome obrigatório, natureza válida)

## 🛠️ Tecnologias de Teste

- **pytest** - Framework de testes
- **pytest-asyncio** - Suporte para testes assíncronos
- **httpx** - Cliente HTTP para TestClient
- **SQLite** - Banco de dados em memória para testes isolados

## 🔧 Fixtures

- `db_engine` - Engine SQLite com suporte a múltiplas threads
- `db_session` - Sessão de banco de dados isolada por teste
- `client` - TestClient do FastAPI com override de dependências
- `tipo_receita` - Tipo de lançamento "Salário" (receita)
- `tipo_despesa` - Tipo de lançamento "Supermercado" (despesa)
- `lancamento_receita` - Lançamento de teste com 1 parcela
- `lancamento_despesa` - Lançamento de teste com 3 parcelas

## 🚀 Como Executar

```bash
# Executar todos os testes
pytest -v

# Executar apenas um arquivo
pytest tests/test_dashboard.py -v

# Executar com cobertura
pytest --cov=app --cov-report=html

# Executar teste específico
pytest tests/test_lancamentos.py::test_criar_lancamento -v
```

## 📈 Melhorias Implementadas

1. **Isolamento de Testes**
   - Banco de dados SQLite em arquivo temporário
   - Configuração `check_same_thread=False` para suporte a múltiplas threads
   - Limpeza automática após cada teste

2. **Fixtures Reutilizáveis**
   - Dados de teste consistentes
   - Setup e teardown automáticos
   - Override de dependências do FastAPI

3. **Testes Abrangentes**
   - CRUD completo
   - Validações de entrada
   - Filtros e queries
   - Exportações (PDF/Excel)
   - Cenários de erro

## 📝 Observações

- Todos os testes são independentes e podem ser executados em qualquer ordem
- O banco de dados é recriado para cada teste, garantindo isolamento total
- Arquivos de teste temporários são automaticamente removidos após a execução
- Os testes cobrem os principais fluxos da aplicação e casos de erro comuns
