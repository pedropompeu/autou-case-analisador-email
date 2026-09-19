# 🚀 Guia de Deploy - Email Analyzer Enterprise

## Pré-requisitos

- Servidor Linux (Ubuntu 20.04+ recomendado)
- Docker & Docker Compose instalados
- Domínio configurado (para produção com HTTPS)
- Chave da API do Google Gemini

## Deploy em Produção

### 1. Preparação do Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
```

### 2. Clone do Repositório

```bash
git clone <repository-url>
cd email-analyzer
```

### 3. Configuração de Ambiente

```bash
# Copiar exemplo de produção
cp .env.production.example .env

# Editar com suas credenciais
nano .env
```

**Variáveis críticas a configurar:**

- `POSTGRES_PASSWORD`: Senha forte para PostgreSQL
- `REDIS_PASSWORD`: Senha para Redis
- `GEMINI_API_KEY`: Sua chave da API do Gemini
- `SECRET_KEY`: Chave secreta (gerar com: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `SENTRY_DSN`: (Opcional) Para monitoramento de erros
- `CORS_ORIGINS`: Domínios permitidos

### 4. Build e Deploy

```bash
# Build das imagens
docker-compose -f docker-compose.prod.yml build

# Iniciar serviços
docker-compose -f docker-compose.prod.yml up -d

# Executar migrações
docker-compose -f docker-compose.prod.yml exec backend flask db upgrade

# Verificar status
docker-compose -f docker-compose.prod.yml ps
```

### 5. Configurar HTTPS (Recomendado)

#### Opção A: Let's Encrypt com Certbot

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Renovação automática (já configurado pelo certbot)
```

#### Opção B: Certificado Próprio

```bash
# Criar diretório para SSL
mkdir ssl

# Copiar certificados
cp /path/to/your/cert.pem ssl/
cp /path/to/your/key.pem ssl/

# Atualizar nginx.conf para usar SSL
```

### 6. Configurar Firewall

```bash
# Permitir HTTP e HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir SSH (se ainda não estiver)
sudo ufw allow 22/tcp

# Ativar firewall
sudo ufw enable
```

### 7. Verificação

```bash
# Health check
curl http://localhost/health

# Ou com domínio
curl https://yourdomain.com/health

# Logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

## Monitoramento

### Logs

```bash
# Ver logs de todos os serviços
docker-compose -f docker-compose.prod.yml logs -f

# Logs específicos
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f postgres
docker-compose -f docker-compose.prod.yml logs -f redis
```

### Métricas

Configure Sentry para monitoramento de erros:

1. Crie conta em [sentry.io](https://sentry.io)
2. Crie novo projeto Flask
3. Copie o DSN
4. Configure `SENTRY_DSN` no `.env`
5. Reinicie o backend

### Health Checks

```bash
# Health check detalhado
curl https://yourdomain.com/api/v1/health

# Status da API
curl https://yourdomain.com/api/v1/status
```

## Backup

### Banco de Dados

```bash
# Backup manual
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U email_analyzer_user email_analyzer_prod > backup_$(date +%Y%m%d).sql

# Restaurar backup
cat backup_20231210.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U email_analyzer_user email_analyzer_prod
```

### Backup Automatizado (Cron)

```bash
# Editar crontab
crontab -e

# Adicionar linha (backup diário às 2h da manhã)
0 2 * * * cd /path/to/email-analyzer && docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U email_analyzer_user email_analyzer_prod > /backups/backup_$(date +\%Y\%m\%d).sql
```

## Atualizações

```bash
# Pull das últimas mudanças
git pull origin main

# Rebuild e restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Executar novas migrações (se houver)
docker-compose -f docker-compose.prod.yml exec backend flask db upgrade
```

## Rollback

```bash
# Voltar para versão anterior do código
git checkout <commit-hash>

# Rebuild
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Reverter migração (se necessário)
# ⚠️  ATENÇÃO: downgrade de migração pode causar PERDA DE DADOS
# dependendo das operações (DROP COLUMN, DROP TABLE, etc.).
# Faça backup ANTES:
docker-compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U email_analyzer_user email_analyzer_prod > rollback_backup_$(date +%Y%m%d_%H%M).sql

# Depois execute o downgrade para uma revisão específica:
docker-compose -f docker-compose.prod.yml exec backend flask db downgrade <revision>
# Exemplo: flask db downgrade -1  (volta uma versão)
```

## Troubleshooting

### Container não inicia

```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs backend

# Verificar configuração
docker-compose -f docker-compose.prod.yml config
```

### Banco de dados não conecta

```bash
# Verificar se PostgreSQL está rodando
docker-compose -f docker-compose.prod.yml ps postgres

# Testar conexão
docker-compose -f docker-compose.prod.yml exec postgres psql -U email_analyzer_user -d email_analyzer_prod -c "SELECT 1;"
```

### Redis não conecta

```bash
# Verificar Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Com senha
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a YOUR_PASSWORD ping
```

### Rate limit não funciona

Verifique se Redis está configurado corretamente e `RATE_LIMIT_ENABLED=true` no `.env`.

### Erro 502 Bad Gateway

- Verificar se backend está rodando: `docker-compose ps backend`
- Verificar logs do nginx: `docker-compose logs nginx`
- Verificar logs do backend: `docker-compose logs backend`

## Segurança

### Checklist de Segurança

- [ ] Senhas fortes configuradas (PostgreSQL, Redis, SECRET_KEY)
- [ ] HTTPS configurado com certificado válido
- [ ] Firewall configurado (apenas portas 80, 443, 22)
- [ ] Rate limiting ativado
- [ ] CORS configurado apenas para domínios necessários
- [ ] Backups automatizados configurados
- [ ] Monitoramento (Sentry) configurado
- [ ] Logs sendo coletados e analisados
- [ ] Atualizações de segurança aplicadas regularmente

### Hardening Adicional

```bash
# Desabilitar root login SSH
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no

# Configurar fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Performance

### Otimizações

1. **Aumentar workers do Gunicorn** (editar Dockerfile.backend):
   ```dockerfile
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", ...]
   ```

2. **Configurar connection pooling** no PostgreSQL

3. **Aumentar cache TTL** se apropriado (config.py)

4. **Usar CDN** para assets estáticos

## Custos Estimados

### Infraestrutura Mínima

- **VPS**: $5-10/mês (DigitalOcean, Linode, Vultr)
- **Domínio**: $10-15/ano
- **SSL**: Grátis (Let's Encrypt)
- **Gemini API**: Pay-as-you-go

### Infraestrutura Recomendada

- **VPS**: $20-40/mês (4GB RAM, 2 vCPUs)
- **Backup Storage**: $5/mês
- **Monitoring (Sentry)**: Grátis até 5k eventos/mês
- **Total**: ~$25-45/mês

## Suporte

Para problemas ou dúvidas:

1. Consulte [CONTRIBUTING.md](CONTRIBUTING.md)
2. Abra uma issue no GitHub
3. Entre em contato com a equipe de desenvolvimento
