# 💰 Sistema Financeiro Pessoal

Sistema completo de gestão financeira pessoal com autenticação, controle de lançamentos, parcelas, metas e relatórios.

## ✨ Funcionalidades

- 🔐 **Autenticação JWT** - Login seguro e controle de acesso
- 💸 **Lançamentos Financeiros** - Receitas e despesas com categorização
- 📊 **Dashboard Interativo** - Gráficos e totalizadores em tempo real
- 📅 **Controle de Parcelas** - Gestão de parcelas a vencer e pagas
- 🔄 **Lançamentos Recorrentes** - Automatização de lançamentos mensais
- 🎯 **Metas Financeiras** - Defina e acompanhe objetivos
- 💳 **Formas de Pagamento** - Cartões, PIX, dinheiro, etc.
- 📈 **Relatórios** - Exportação para Excel e PDF
- 🔒 **Multi-tenant** - Dados isolados por usuário
- 📱 **PWA Ready** - Funciona offline como app

## 🚀 Quick Start

### Desenvolvimento Local

```bash
# Clone o repositório
git clone https://github.com/SEU-USUARIO/sistema-financeiro-pessoal.git
cd sistema-financeiro-pessoal

# Crie e ative o ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
copy .env.example .env
# Edite .env e defina SECRET_KEY

# Inicialize o banco de dados
python init_db.py

# Rode o servidor
python start_server.py
```

Acesse: http://localhost:8000

**Login padrão:**
- Email: `admin@sistema.com`
- Senha: `admin123`

### Deploy na Nuvem ☁️

Escolha uma opção:

**🚄 Railway (Recomendado - Mais Rápido):**
```powershell
.\setup-git.ps1
# Depois: Deploy no Railway (veja QUICKSTART-DEPLOY.md)
```

**📖 Documentação Completa:**
- [QUICKSTART-DEPLOY.md](./QUICKSTART-DEPLOY.md) - Deploy em 5 minutos
- [DEPLOY.md](./DEPLOY.md) - Guia completo e detalhado

## 🧪 Testes

```bash
# Rodar todos os testes
python run_tests.py

# Ou com pytest diretamente
pytest -v

# Com coverage
pytest --cov=app tests/
```

## 📚 Estrutura do Projeto

```
sistema-financeiro-pessoal/
├── app/
│   ├── main.py              # Aplicação FastAPI principal
│   ├── auth.py              # Módulo de autenticação
│   ├── middleware.py        # Middlewares (auth, security)
│   ├── templates/           # Templates Jinja2
│   └── static/              # CSS, JS, ícones
├── tests/                   # Testes automatizados
├── data/                    # Banco SQLite (gitignored)
├── backups/                 # Backups automáticos
├── .env.example             # Exemplo de variáveis de ambiente
├── requirements.txt         # Dependências Python
├── Dockerfile.production    # Docker para produção
├── railway.json             # Config Railway
├── render.yaml              # Config Render
├── fly.toml                 # Config Fly.io
└── DEPLOY.md                # Documentação de deploy

```

## 🔧 Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```bash
# Segurança (obrigatório em produção)
SECRET_KEY=sua-chave-secreta-aqui
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Banco de Dados
DB_PATH=lancamentos.db

# Servidor
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# Logs
LOG_LEVEL=info
```

**Gerar SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🛡️ Segurança

- ✅ Autenticação JWT com tokens seguros
- ✅ Senhas hash com bcrypt
- ✅ CSP (Content Security Policy)
- ✅ HSTS em produção
- ✅ Rate limiting em endpoints sensíveis
- ✅ Isolamento multi-tenant rigoroso
- ✅ Validação de inputs com Pydantic v2

## 📊 Tecnologias

- **Backend:** FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Auth:** python-jose (JWT), passlib (bcrypt)
- **Frontend:** Jinja2, Chart.js, Vanilla JS
- **Database:** SQLite (dev), PostgreSQL ready
- **Testes:** pytest, pytest-asyncio
- **Deploy:** Railway, Render, Fly.io

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Scripts Úteis

```bash
# Inicializar banco de dados
python init_db.py

# Resetar banco (cuidado!)
python reset_db.py

# Criar dados de demonstração
python seed_demo_data.py

# Executar testes
python run_tests.py

# Criar backup manual
python -c "from app.main import criar_backup; print(criar_backup())"
```

## 🐛 Troubleshooting

### Erro: "Application failed to start"
- Verifique se `SECRET_KEY` está configurada
- Confirme que todas as dependências estão instaladas
- Veja logs: `LOG_LEVEL=debug python start_server.py`

### Database locked
- SQLite tem limitações de concorrência
- Para produção com múltiplos usuários, use PostgreSQL

### Testes falhando
- Confirme que está no ambiente virtual: `.venv/Scripts/Activate.ps1`
- Reinstale dependências: `pip install -r requirements.txt`
- Limpe cache: `pytest --cache-clear`

## 📄 Licença

Este projeto é privado. Todos os direitos reservados.

## 🆘 Suporte

- 📧 Email: seu-email@exemplo.com
- 🐛 Issues: [GitHub Issues](https://github.com/SEU-USUARIO/sistema-financeiro-pessoal/issues)
- 📖 Docs: Veja arquivos `.md` no repositório

---

**Desenvolvido com ❤️ usando FastAPI**
