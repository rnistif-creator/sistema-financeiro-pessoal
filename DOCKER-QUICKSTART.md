# ⚡ Quick Start - Docker

## 📋 Passo a Passo

### 1️⃣ Iniciar Docker Desktop

**⚠️ IMPORTANTE:** O Docker Desktop precisa estar rodando!

1. Procure "Docker Desktop" no menu Iniciar
2. Clique para abrir
3. Aguarde o ícone na bandeja ficar **verde** ✅
4. Pode levar 1-2 minutos na primeira vez

**Como saber se está rodando?**
- Ícone da baleia na bandeja do sistema (próximo ao relógio)
- Ícone verde = rodando ✅
- Ícone cinza/vermelho = parado ❌

---

### 2️⃣ Construir a Imagem Docker

Abra o PowerShell **nesta pasta** e execute:

```powershell
docker-compose build
```

**Isso vai:**
- Baixar a imagem base do Python (pode demorar na primeira vez)
- Instalar todas as dependências
- Criar a imagem do sistema
- ⏱️ Tempo: 2-5 minutos na primeira vez

---

### 3️⃣ Iniciar o Sistema

```powershell
docker-compose up -d
```

**O que acontece:**
- Container é criado e iniciado
- Sistema fica rodando em background
- ✅ Pronto em ~10 segundos

---

### 4️⃣ Acessar

Abra o navegador em: **http://localhost:8001**

---

## 🎯 Comandos Essenciais

```powershell
# Ver se está rodando
docker-compose ps

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Reiniciar
docker-compose restart
```

---

## 🚀 Método Alternativo: Script Interativo

Execute:
```powershell
.\docker-manager.ps1
```

Menu interativo com todas as opções! 🎉

---

## ❓ Problemas Comuns

### "Docker não está rodando"
**Solução:** Abra o Docker Desktop e aguarde ficar verde

### "Porta 8001 em uso"
**Solução 1:** Pare o servidor Python normal
```powershell
Stop-Process -Name python -Force
```

**Solução 2:** Use outra porta
- Edite `docker-compose.yml`
- Mude `ports: - "8080:8001"` (acesse via 8080)

### "Permission denied"
**Solução:** Execute o PowerShell como Administrador

---

## 📦 Após Construir a Imagem

Você só precisa construir **UMA VEZ**!

Depois, para usar:
```powershell
docker-compose up -d      # Iniciar
# ... usar o sistema ...
docker-compose down       # Parar
```

Rebuild só é necessário se:
- Atualizar o código
- Mudar dependências (requirements.txt)
- Modificar o Dockerfile

---

## 💾 Seus Dados

**Onde ficam:**
- `./data/lancamentos.db` - Banco de dados
- `./backups/` - Backups

**⚠️ São persistentes!** Mesmo parando/removendo o container, os dados ficam salvos.

---

## 🎉 Pronto!

Agora você tem:
- ✅ Sistema containerizado
- ✅ Funciona em qualquer máquina
- ✅ Fácil de colocar online
- ✅ Fácil de compartilhar
- ✅ Isolado e seguro

**🐳 Bem-vindo ao mundo Docker!**

---

## 📚 Documentação Completa

Veja `DOCKER.md` para instruções avançadas:
- Deploy em servidor
- Configurações avançadas
- Troubleshooting completo
- Dicas de performance
- E muito mais!
