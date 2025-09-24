# Guia de Deploy para Produção - Ferramenta Paiol

Este guia fornece instruções detalhadas para fazer o deploy do projeto Django "Ferramenta Paiol" em diferentes plataformas de hospedagem.

## Índice

1. [Preparação para Deploy](#preparação-para-deploy)
2. [Deploy no Heroku (Recomendado para iniciantes)](#deploy-no-heroku)
3. [Deploy no DigitalOcean App Platform](#deploy-no-digitalocean-app-platform)
4. [Deploy em VPS (Ubuntu/Linux)](#deploy-em-vps)
5. [Deploy no Railway](#deploy-no-railway)
6. [Configurações de Produção](#configurações-de-produção)
7. [Criação de Usuários Iniciais](#criação-de-usuários-iniciais)
8. [Manutenção e Monitoramento](#manutenção-e-monitoramento)

---

## Preparação para Deploy

Antes de fazer o deploy, certifique-se de que o projeto está pronto para produção.

### 1. Configurações de Segurança

Edite o arquivo `camp_project/settings.py`:

```python
import os
from pathlib import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'sua-chave-secreta-aqui')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'seu-dominio.com',  # Substitua pelo seu domínio
    '.herokuapp.com',   # Para Heroku
    '.railway.app',     # Para Railway
    '.ondigitalocean.app',  # Para DigitalOcean
]

# Database para produção
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'ferramenta_paiol'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Para desenvolvimento local, use SQLite
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Configurações de arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configurações de segurança para produção
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

### 2. Arquivo requirements.txt

Crie/atualize o arquivo `requirements.txt`:

```txt
Django==4.2.7
psycopg2-binary==2.9.7
gunicorn==21.2.0
whitenoise==6.6.0
python-decouple==3.8
dj-database-url==2.1.0
```

### 3. Arquivo Procfile (para Heroku/Railway)

Crie um arquivo `Procfile` na raiz do projeto:

```
web: gunicorn camp_project.wsgi --log-file -
```

### 4. Arquivo runtime.txt (para Heroku)

Crie um arquivo `runtime.txt`:

```
python-3.11.0
```

---


## Deploy no Heroku

O Heroku é uma das opções mais simples para deploy de aplicações Django.

### Pré-requisitos

1. Conta no [Heroku](https://heroku.com)
2. [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) instalado
3. Git configurado

### Passo a Passo

#### 1. Preparar o projeto

```bash
# Instalar dependências
pip install gunicorn whitenoise psycopg2-binary

# Atualizar requirements.txt
pip freeze > requirements.txt
```

#### 2. Configurar Whitenoise para arquivos estáticos

Adicione no `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Adicione esta linha
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... resto do middleware
]

# Configuração do Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### 3. Criar aplicação no Heroku

```bash
# Login no Heroku
heroku login

# Criar aplicação (substitua 'meu-app-paiol' por um nome único)
heroku create meu-app-paiol

# Adicionar PostgreSQL
heroku addons:create heroku-postgresql:mini
```

#### 4. Configurar variáveis de ambiente

```bash
# Gerar uma SECRET_KEY segura
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Configurar variáveis no Heroku
heroku config:set SECRET_KEY="sua-secret-key-gerada"
heroku config:set DEBUG=False
heroku config:set DJANGO_SETTINGS_MODULE=camp_project.settings
```

#### 5. Deploy

```bash
# Adicionar remote do Heroku (se não foi feito automaticamente)
heroku git:remote -a meu-app-paiol

# Fazer commit das alterações
git add .
git commit -m "Preparar para deploy no Heroku"

# Deploy
git push heroku main

# Executar migrações
heroku run python manage.py migrate

# Criar superusuário
heroku run python manage.py createsuperuser

# Coletar arquivos estáticos
heroku run python manage.py collectstatic --noinput
```

#### 6. Abrir aplicação

```bash
heroku open
```

### Configurações Adicionais para Heroku

Adicione no `settings.py`:

```python
import dj_database_url

# Database configuration for Heroku
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])
```

---

## Deploy no DigitalOcean App Platform

O DigitalOcean App Platform oferece uma solução simples e escalável.

### Pré-requisitos

1. Conta no [DigitalOcean](https://digitalocean.com)
2. Repositório Git (GitHub, GitLab, etc.)

### Passo a Passo

#### 1. Preparar o projeto

Crie um arquivo `.do/app.yaml` na raiz do projeto:

```yaml
name: ferramenta-paiol
services:
- name: web
  source_dir: /
  github:
    repo: seu-usuario/ferramenta_paiol
    branch: main
  run_command: gunicorn --worker-tmp-dir /dev/shm camp_project.wsgi
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    value: "sua-secret-key"
    type: SECRET
  - key: DJANGO_SETTINGS_MODULE
    value: "camp_project.settings"

databases:
- name: db
  engine: PG
  version: "13"
  size_slug: db-s-dev-database
```

#### 2. Deploy via Interface Web

1. Acesse o [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Clique em "Create App"
3. Conecte seu repositório GitHub/GitLab
4. Configure as variáveis de ambiente
5. Adicione um banco PostgreSQL
6. Clique em "Create Resources"

#### 3. Configurar após deploy

```bash
# Conectar via console do DigitalOcean ou usar doctl
doctl apps create-deployment <app-id>

# Executar migrações (via console web)
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---


## Deploy em VPS (Ubuntu/Linux)

Para maior controle e customização, você pode usar um VPS.

### Pré-requisitos

1. VPS com Ubuntu 20.04+ (DigitalOcean, Linode, AWS EC2, etc.)
2. Acesso SSH ao servidor
3. Domínio configurado (opcional)

### Passo a Passo

#### 1. Configurar o servidor

```bash
# Conectar ao servidor
ssh root@seu-servidor-ip

# Atualizar sistema
apt update && apt upgrade -y

# Instalar dependências
apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib git -y

# Criar usuário para a aplicação
adduser django
usermod -aG sudo django
su - django
```

#### 2. Configurar PostgreSQL

```bash
# Conectar como postgres
sudo -u postgres psql

# Criar banco e usuário
CREATE DATABASE ferramenta_paiol;
CREATE USER django_user WITH PASSWORD 'senha_segura';
ALTER ROLE django_user SET client_encoding TO 'utf8';
ALTER ROLE django_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE django_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ferramenta_paiol TO django_user;
\q
```

#### 3. Configurar aplicação

```bash
# Clonar repositório
cd /home/django
git clone https://github.com/seu-usuario/ferramenta_paiol.git
cd ferramenta_paiol

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
nano .env
```

Conteúdo do arquivo `.env`:

```env
SECRET_KEY=sua-secret-key-muito-segura
DEBUG=False
DB_NAME=ferramenta_paiol
DB_USER=django_user
DB_PASSWORD=senha_segura
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com,seu-ip
```

#### 4. Configurar Django

```bash
# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

#### 5. Configurar Gunicorn

```bash
# Testar Gunicorn
gunicorn --bind 0.0.0.0:8000 camp_project.wsgi

# Criar arquivo de serviço
sudo nano /etc/systemd/system/gunicorn.service
```

Conteúdo do arquivo de serviço:

```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/ferramenta_paiol
ExecStart=/home/django/ferramenta_paiol/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          camp_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Criar socket do Gunicorn
sudo nano /etc/systemd/system/gunicorn.socket
```

Conteúdo do socket:

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

```bash
# Ativar serviços
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

#### 6. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/ferramenta_paiol
```

Conteúdo da configuração do Nginx:

```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/django/ferramenta_paiol;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/ferramenta_paiol /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# Configurar firewall
sudo ufw allow 'Nginx Full'
```

#### 7. SSL com Let's Encrypt (Opcional)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Testar renovação automática
sudo certbot renew --dry-run
```

---

## Deploy no Railway

O Railway é uma plataforma moderna e simples para deploy.

### Passo a Passo

#### 1. Preparar o projeto

Crie um arquivo `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn camp_project.wsgi",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. Deploy

1. Acesse [Railway](https://railway.app)
2. Conecte seu repositório GitHub
3. Adicione PostgreSQL plugin
4. Configure variáveis de ambiente:
   - `SECRET_KEY`: sua chave secreta
   - `DEBUG`: False
   - `DJANGO_SETTINGS_MODULE`: camp_project.settings

#### 3. Configurar após deploy

Use o Railway CLI ou interface web para executar:

```bash
python manage.py createsuperuser
```

---

## Configurações de Produção

### Variáveis de Ambiente Essenciais

```env
SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria
DEBUG=False
DJANGO_SETTINGS_MODULE=camp_project.settings
DB_NAME=ferramenta_paiol
DB_USER=usuario_db
DB_PASSWORD=senha_segura_db
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
```

### Configurações de Email (Opcional)

Para funcionalidades de email, adicione:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=seu-email@gmail.com
```

---


## Criação de Usuários Iniciais

Após o deploy, você precisará criar os usuários iniciais do sistema.

### 1. Criar Superusuário (Admin)

```bash
# Via comando Django
python manage.py createsuperuser

# Ou via shell Django
python manage.py shell
```

```python
from core.models import CustomUser

# Criar superusuário
admin = CustomUser.objects.create_superuser(
    username='admin',
    email='admin@seudominio.com',
    password='senha_muito_segura',
    user_type='admin',
    first_name='Administrador',
    last_name='Sistema'
)
```

### 2. Criar Usuário Gestor

```python
# Via shell Django
from core.models import CustomUser

gestor = CustomUser.objects.create_user(
    username='gestor',
    email='gestor@seudominio.com',
    password='senha_segura_gestor',
    user_type='gestor',
    first_name='Nome do Gestor',
    last_name='Sobrenome',
    cpf='000.000.000-00',
    telefone='(11) 99999-9999'
)
```

### 3. Script para Criação em Lote

Crie um arquivo `create_initial_users.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'camp_project.settings')
django.setup()

from core.models import CustomUser

# Dados dos usuários iniciais
users_data = [
    {
        'username': 'admin',
        'email': 'admin@seudominio.com',
        'password': 'senha_admin_segura',
        'user_type': 'admin',
        'first_name': 'Administrador',
        'last_name': 'Sistema',
        'is_superuser': True,
        'is_staff': True
    },
    {
        'username': 'gestor1',
        'email': 'gestor@seudominio.com',
        'password': 'senha_gestor_segura',
        'user_type': 'gestor',
        'first_name': 'Nome do Gestor',
        'last_name': 'Sobrenome',
        'cpf': '000.000.000-00',
        'telefone': '(11) 99999-9999'
    }
]

for user_data in users_data:
    if not CustomUser.objects.filter(username=user_data['username']).exists():
        password = user_data.pop('password')
        is_superuser = user_data.pop('is_superuser', False)
        is_staff = user_data.pop('is_staff', False)
        
        if is_superuser:
            user = CustomUser.objects.create_superuser(**user_data)
        else:
            user = CustomUser.objects.create_user(**user_data)
            
        user.set_password(password)
        user.is_staff = is_staff
        user.save()
        
        print(f"Usuário {user.username} criado com sucesso!")
    else:
        print(f"Usuário {user_data['username']} já existe.")
```

Execute o script:

```bash
python create_initial_users.py
```

---

## Manutenção e Monitoramento

### Comandos Úteis de Manutenção

#### Backup do Banco de Dados

```bash
# PostgreSQL
pg_dump -h localhost -U usuario_db ferramenta_paiol > backup_$(date +%Y%m%d_%H%M%S).sql

# Para Heroku
heroku pg:backups:capture
heroku pg:backups:download
```

#### Logs da Aplicação

```bash
# Heroku
heroku logs --tail

# VPS com systemd
sudo journalctl -u gunicorn -f

# Railway
railway logs
```

#### Atualizações

```bash
# Fazer backup antes de atualizar
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Reiniciar serviços (VPS)
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Monitoramento

#### Métricas Importantes

1. **Tempo de resposta da aplicação**
2. **Uso de CPU e memória**
3. **Espaço em disco**
4. **Conexões de banco de dados**
5. **Logs de erro**

#### Ferramentas Recomendadas

- **Sentry**: Para monitoramento de erros
- **New Relic**: Para performance
- **Uptime Robot**: Para monitoramento de disponibilidade
- **Google Analytics**: Para métricas de uso

### Configuração do Sentry (Opcional)

```bash
pip install sentry-sdk[django]
```

Adicione no `settings.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn="sua-dsn-do-sentry",
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )
```

---

## Checklist Final

Antes de considerar o deploy completo, verifique:

- [ ] ✅ Aplicação funcionando corretamente
- [ ] ✅ SSL configurado (HTTPS)
- [ ] ✅ Banco de dados configurado e com backup
- [ ] ✅ Usuários iniciais criados
- [ ] ✅ Arquivos estáticos servindo corretamente
- [ ] ✅ Logs configurados
- [ ] ✅ Monitoramento ativo
- [ ] ✅ Variáveis de ambiente seguras
- [ ] ✅ DEBUG=False em produção
- [ ] ✅ Domínio configurado
- [ ] ✅ Email funcionando (se aplicável)

---

## Suporte

Para dúvidas ou problemas:

1. Verifique os logs da aplicação
2. Consulte a documentação do Django
3. Verifique as configurações de ambiente
4. Entre em contato com o desenvolvedor

**Importante**: Mantenha sempre backups atualizados e teste as atualizações em ambiente de desenvolvimento antes de aplicar em produção.

---

*Guia criado para o projeto Ferramenta Paiol - Sistema de Gerenciamento de Acampamentos*

