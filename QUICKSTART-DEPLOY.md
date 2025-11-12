# 🚀 Quick Start - Deploy em 5 Minutos

## Opção 1: Railway (Mais Rápido) ⚡

1. **Executar script Git:**
   ```powershell
   .\setup-git.ps1
   ```

2. **Deploy no Railway:**
   - Acesse: https://railway.app
   - Login com GitHub
   - "New Project" → "Deploy from GitHub repo"
   - Selecione `sistema-financeiro-pessoal`
   - Adicione variável: `SECRET_KEY` (gere com comando abaixo)
   - Deploy automático!

3. **Gerar SECRET_KEY:**
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

✅ **Pronto!** Acesse o domínio gerado pelo Railway.

---

## Opção 2: Render (Free Forever) 💚

1. **Executar script Git:**
   ```powershell
   .\setup-git.ps1
   ```

2. **Deploy no Render:**
   - Acesse: https://render.com
   - "New" → "Web Service"
   - Conecte seu repositório
   - Render detecta `render.yaml` automaticamente
   - Adicione `SECRET_KEY` nas variáveis
   - Deploy!

3. **Adicionar Disco Persistente:**
   - Settings → Disks
   - Add Disk: `data` → `/opt/render/project/src/data` → `1 GB`

✅ **Pronto!** Acesse o domínio `.onrender.com`.

---

## Opção 3: Fly.io (Global) 🌍

1. **Instalar CLI:**
   ```powershell
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Executar script Git:**
   ```powershell
   .\setup-git.ps1
   ```

3. **Deploy:**
   ```bash
   fly auth login
   fly launch --no-deploy
   fly volumes create data --size 1
   fly secrets set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   fly deploy
   fly open
   ```

✅ **Pronto!** Aplicação rodando globalmente.

---

## 📝 Checklist Mínimo

- [ ] Git inicializado e código no GitHub
- [ ] Plataforma cloud escolhida
- [ ] `SECRET_KEY` configurada
- [ ] Deploy realizado
- [ ] Teste de login funcionando

---

## 🆘 Problemas Comuns

**"Authentication failed" no Git:**
```bash
# Configure suas credenciais
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

**"Application failed to start":**
- Verifique se `SECRET_KEY` está configurada na plataforma
- Veja logs da plataforma para detalhes

**"Database locked":**
- Normal com SQLite em free tiers
- Considere PostgreSQL se persistir

---

## 📚 Documentação Completa

Para instruções detalhadas, veja **[DEPLOY.md](./DEPLOY.md)**.

---

**Dúvidas?** Abra uma issue no GitHub! 🎯
