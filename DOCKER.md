# 🐳 Docker - Sistema Financeiro Pessoal

Guia completo para usar o Sistema Financeiro Pessoal com Docker.

## 📋 Pré-requisitos

### Instalar Docker

#### Windows
1. Baixe [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop)
2. Instale e reinicie o computador
3. Abra o Docker Desktop
4. Aguarde o Docker iniciar (ícone na bandeja ficará verde)

#### Mac
1. Baixe [Docker Desktop para Mac](https://www.docker.com/products/docker-desktop)
2. Instale arrastando para a pasta Applications
3. Abra o Docker Desktop
4. Aguarde iniciar

#### Linux (Ubuntu/Debian)
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar sessão ou executar
newgrp docker
```

### Verificar Instalação

```bash
docker --version
docker-compose --version
```

---

## 🚀 Início Rápido

### Método 1: Script Interativo (Recomendado)

#### Windows (PowerShell)
```powershell
.\docker-manager.ps1
```

#### Linux/Mac
```bash
chmod +x docker-manager.sh
./docker-manager.sh
```

O script oferece um menu interativo com todas as opções necessárias!

### Método 2: Comandos Manuais

#### 1. Construir a Imagem
```bash
docker-compose build
```

#### 2. Iniciar a Aplicação
```bash
docker-compose up -d
```

#### 3. Verificar Status
```bash
docker-compose ps
```

#### 4. Acessar
Abra seu navegador em: **http://localhost:8001**

---

## 📦 Comandos Úteis

### Gerenciamento Básico

```bash
# Iniciar (em background)
docker-compose up -d

# Parar
docker-compose down

# Reiniciar
docker-compose restart

# Ver logs em tempo real
docker-compose logs -f

# Ver status
docker-compose ps
```

### Debug e Acesso

```bash
# Acessar shell do container
docker-compose exec app /bin/bash

# Ver logs específicos
docker-compose logs app --tail=100

# Executar comando no container
docker-compose exec app python diagnose.py
```

### Banco de Dados

```bash
# Inicializar banco de dados
docker-compose exec app python init_db.py

# Backup do banco
docker cp sistema-financeiro:/app/data/lancamentos.db ./backup-$(date +%Y%m%d).db

# Restaurar backup
docker cp ./backup.db sistema-financeiro:/app/data/lancamentos.db
```

### Limpeza

```bash
# Parar e remover containers
docker-compose down

# Remover containers + volumes
docker-compose down -v

# Remover imagem
docker rmi sistema-financeiro:latest

# Limpeza geral do Docker
docker system prune -a
```

---

## 📂 Estrutura de Volumes

O Docker persiste dados importantes em volumes:

```
./data/              # Banco de dados SQLite
./backups/           # Backups automáticos
./logs/              # Logs da aplicação (se habilitado)
```

**⚠️ IMPORTANTE:** Não delete essas pastas! Elas contêm seus dados financeiros.

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Edite o arquivo `docker-compose.yml` para configurar:

```yaml
environment:
  - DB_PATH=/app/data/lancamentos.db    # Caminho do banco
  - ENVIRONMENT=production               # Modo de execução
  - LOG_LEVEL=info                       # Nível de log (debug/info/warning/error)
```

### Mudar Porta

No `docker-compose.yml`:

```yaml
ports:
  - "8080:8001"  # Acessar via http://localhost:8080
```

### Limites de Recursos

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Máximo de 2 CPUs
      memory: 1G       # Máximo de 1GB RAM
```

---

## 🌐 Deploy em Servidor

### VPS/Cloud (DigitalOcean, AWS, Azure, etc)

1. **Conectar ao servidor**
```bash
ssh usuario@seu-servidor.com
```

2. **Instalar Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

3. **Clonar/Copiar projeto**
```bash
git clone seu-repositorio.git
# ou
scp -r ./sistema-financeiro usuario@servidor:/home/usuario/
```

4. **Iniciar**
```bash
cd sistema-financeiro
docker-compose up -d
```

5. **Configurar domínio (opcional)**
Use nginx ou Caddy como reverse proxy:

```nginx
server {
    listen 80;
    server_name financeiro.seudominio.com;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🐳 Docker Hub (Compartilhar Imagem)

### Publicar no Docker Hub

1. **Criar conta em** [hub.docker.com](https://hub.docker.com)

2. **Login**
```bash
docker login
```

3. **Tag da imagem**
```bash
docker tag sistema-financeiro:latest seu-usuario/sistema-financeiro:latest
```

4. **Push**
```bash
docker push seu-usuario/sistema-financeiro:latest
```

### Usar imagem do Docker Hub

```bash
docker pull seu-usuario/sistema-financeiro:latest
docker run -d -p 8001:8001 seu-usuario/sistema-financeiro:latest
```

---

## 🔍 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs

# Verificar se a porta está em uso
# Windows
netstat -ano | findstr :8001
# Linux/Mac
lsof -i :8001

# Parar processo que está usando a porta
# Windows
taskkill /PID <PID> /F
# Linux/Mac
kill -9 <PID>
```

### Erros de permissão (Linux)

```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Corrigir permissões das pastas
sudo chown -R $USER:$USER ./data ./backups
```

### Container reiniciando constantemente

```bash
# Ver logs do healthcheck
docker inspect sistema-financeiro

# Desabilitar healthcheck temporariamente
# Comente as linhas de healthcheck no docker-compose.yml
```

### Rebuild completo

```bash
# Parar tudo
docker-compose down -v

# Rebuild sem cache
docker-compose build --no-cache

# Iniciar novamente
docker-compose up -d
```

---

## 📊 Monitoramento

### Ver uso de recursos

```bash
# Estatísticas em tempo real
docker stats sistema-financeiro

# Uso de disco
docker system df
```

### Healthcheck

O container possui healthcheck automático:
- Verifica a cada 30 segundos
- Considera saudável se responder em até 10 segundos
- Marca como unhealthy após 3 falhas consecutivas

```bash
# Ver status de saúde
docker inspect --format='{{.State.Health.Status}}' sistema-financeiro
```

---

## 🔄 Atualizações

### Atualizar aplicação

```bash
# 1. Parar container
docker-compose down

# 2. Atualizar código (git pull ou copiar novos arquivos)
git pull

# 3. Rebuild
docker-compose build

# 4. Iniciar
docker-compose up -d
```

### Manter dados ao atualizar

Os volumes `./data` e `./backups` são persistentes. Suas atualizações não afetarão os dados!

---

## 💡 Dicas

### Performance
- Use volumes nomeados em produção para melhor performance
- Limite recursos conforme necessidade do servidor
- Habilite logs rotativos para não encher disco

### Segurança
- Não exponha porta 8001 diretamente na internet
- Use reverse proxy (nginx/Caddy) com SSL
- Faça backups regulares da pasta `./data`
- Nunca commite o arquivo `.env` com senhas no Git

### Desenvolvimento
- Para desenvolvimento, use `docker-compose up` (sem -d) para ver logs
- Monte o código como volume para hot-reload:
  ```yaml
  volumes:
    - ./app:/app/app  # Hot reload
  ```

---

## 📞 Suporte

### Verificar versões
```bash
docker --version
docker-compose --version
python --version  # Dentro do container
```

### Reset completo
```bash
# ⚠️ CUIDADO: Apaga TUDO (inclusive dados)!
docker-compose down -v
docker rmi sistema-financeiro:latest -f
docker system prune -a -f
```

---

## 📚 Recursos Adicionais

- [Documentação Docker](https://docs.docker.com)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)

---

**🎉 Pronto! Seu sistema está containerizado e pronto para rodar em qualquer lugar!**
