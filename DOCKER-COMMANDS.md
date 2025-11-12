# ⚡ Comandos Rápidos - Copy & Paste

## 🚀 Setup Inicial (Execute em ordem)

### 1. Build (primeira vez - demora 2-5min)
```powershell
docker-compose build
```

### 2. Iniciar
```powershell
docker-compose up -d
```

### 3. Verificar
```powershell
docker-compose ps
```

### 4. Ver logs
```powershell
docker-compose logs -f
```

---

## 📊 Comandos do Dia a Dia

### Iniciar sistema
```powershell
docker-compose up -d
```

### Parar sistema
```powershell
docker-compose down
```

### Reiniciar sistema
```powershell
docker-compose restart
```

### Ver status
```powershell
docker-compose ps
```

### Ver logs em tempo real
```powershell
docker-compose logs -f
```

### Ver últimas 100 linhas de log
```powershell
docker-compose logs --tail=100
```

---

## 🔧 Manutenção

### Entrar no container
```powershell
docker-compose exec app /bin/bash
```

### Ver uso de recursos
```powershell
docker stats sistema-financeiro
```

### Rebuild (após atualizar código)
```powershell
docker-compose down
docker-compose build
docker-compose up -d
```

### Rebuild sem cache (se der problema)
```powershell
docker-compose build --no-cache
```

---

## 💾 Backup e Restauração

### Backup do banco de dados
```powershell
# Copia do container para o host
docker cp sistema-financeiro:/app/data/lancamentos.db ./backup-$(Get-Date -Format "yyyyMMdd_HHmmss").db
```

### Restaurar backup
```powershell
# Copia do host para o container
docker cp ./backup.db sistema-financeiro:/app/data/lancamentos.db
docker-compose restart
```

### Backup completo (container + dados)
```powershell
# Salvar imagem
docker save sistema-financeiro:latest -o sistema-financeiro.tar

# Carregar imagem
docker load -i sistema-financeiro.tar
```

---

## 🧹 Limpeza

### Parar e remover container
```powershell
docker-compose down
```

### Parar e remover container + volumes
```powershell
docker-compose down -v
```

### Remover imagem
```powershell
docker rmi sistema-financeiro:latest
```

### Limpeza geral (remove tudo não usado)
```powershell
docker system prune -a
```

### Limpeza completa (CUIDADO: remove volumes)
```powershell
docker system prune -a --volumes
```

---

## 🐛 Troubleshooting

### Ver processos rodando
```powershell
docker ps -a
```

### Ver imagens disponíveis
```powershell
docker images
```

### Inspecionar container
```powershell
docker inspect sistema-financeiro
```

### Ver logs de erro
```powershell
docker-compose logs --tail=50 | Select-String "error"
```

### Forçar parada
```powershell
docker-compose kill
docker-compose down
```

### Verificar Docker está rodando
```powershell
docker info
```

### Reiniciar Docker Desktop (Windows)
```powershell
Restart-Service docker
```

---

## 🌐 Rede e Portas

### Ver portas em uso
```powershell
docker port sistema-financeiro
```

### Testar conexão
```powershell
Invoke-WebRequest -Uri "http://localhost:8001" -UseBasicParsing
```

### Ver todas as redes Docker
```powershell
docker network ls
```

---

## 📦 Deploy

### Tag para Docker Hub
```powershell
docker tag sistema-financeiro:latest seu-usuario/sistema-financeiro:latest
```

### Push para Docker Hub
```powershell
docker login
docker push seu-usuario/sistema-financeiro:latest
```

### Pull e Run de imagem remota
```powershell
docker pull seu-usuario/sistema-financeiro:latest
docker run -d -p 8001:8001 --name sistema-financeiro seu-usuario/sistema-financeiro:latest
```

---

## 🔄 Atualização

### Parar → Atualizar código → Rebuild → Iniciar
```powershell
docker-compose down
git pull
docker-compose build
docker-compose up -d
```

### Atualização sem downtime (requer 2 instâncias)
```powershell
docker-compose up -d --scale app=2
docker-compose build
docker-compose up -d --no-deps app
```

---

## 📊 Monitoramento

### Stats em tempo real
```powershell
docker stats sistema-financeiro
```

### Uso de disco
```powershell
docker system df
```

### Ver processos dentro do container
```powershell
docker-compose exec app ps aux
```

### Healthcheck status
```powershell
docker inspect --format='{{.State.Health.Status}}' sistema-financeiro
```

---

## 🎯 Script Interativo (Recomendado!)

### Windows
```powershell
.\docker-manager.ps1
```

### Linux/Mac
```bash
chmod +x docker-manager.sh
./docker-manager.sh
```

**Menu completo com todas as opções! 🎮**

---

## 💡 Dicas

### Alias úteis (adicione ao seu $PROFILE)
```powershell
# PowerShell Profile: notepad $PROFILE

# Alias para comandos Docker comuns
Set-Alias -Name dc -Value docker-compose
Set-Alias -Name dps -Value "docker-compose ps"
Set-Alias -Name dlogs -Value "docker-compose logs -f"

# Funções úteis
function dcup { docker-compose up -d }
function dcdown { docker-compose down }
function dcrestart { docker-compose restart }
function dcbuild { docker-compose build }
```

### Variáveis de ambiente úteis
```powershell
# Ver todas as variáveis do container
docker-compose exec app env

# Executar com variável específica
docker-compose run -e DEBUG=true app python diagnose.py
```

---

## 🆘 Emergência - Reset Total

### Se TUDO der errado:
```powershell
# 1. Parar tudo
docker-compose down -v

# 2. Remover imagem
docker rmi sistema-financeiro:latest -f

# 3. Limpar sistema
docker system prune -a -f

# 4. Recomeçar
docker-compose build
docker-compose up -d
```

**⚠️ ATENÇÃO:** Isso remove os dados! Faça backup antes se necessário.

---

## 📞 Suporte Rápido

### Comandos de diagnóstico para suporte
```powershell
# Informações completas
docker --version
docker-compose --version
docker info
docker-compose ps
docker-compose logs --tail=50
docker inspect sistema-financeiro
```

---

**🎉 Pronto! Copie e cole os comandos conforme necessário!**
