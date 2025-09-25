# 🐍 Deploy no PythonAnywhere - Ferramenta Paiol

## 📋 **Pré-requisitos**
- Conta no [PythonAnywhere](https://www.pythonanywhere.com)
- Conta no GitHub
- Projeto na branch `feature/prod`

---

## 🎯 **Passo a Passo - PythonAnywhere**

### **1. Criar Conta e Configurar**
1. Acesse [pythonanywhere.com](https://www.pythonanywhere.com)
2. Crie conta gratuita (Beginner Account)
3. Acesse o **Dashboard**

### **2. Clonar o Repositório**
No **Console** do PythonAnywhere:
```bash
# Navegar para home
cd ~

# Clonar repositório
git clone https://github.com/seu-usuario/ferramenta_paiol.git
cd ferramenta_paiol

# Mudar para branch de produção
git checkout feature/prod
```

### **3. Criar Ambiente Virtual**
```bash
# Criar ambiente virtual
python3.11 -m venv venv

# Ativar ambiente
source venv/bin/activate

# Instalar dependências
pip install -r requirements_prod.txt
```

### **4. Configurar Variáveis de Ambiente**
Criar arquivo `.env`:
```bash
# Criar arquivo de ambiente
nano .env
```

Adicionar conteúdo:
```env
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
DJANGO_SETTINGS_MODULE=camp_project.settings_prod
HOSTING_PROVIDER=pythonanywhere

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### **5. Configurar Banco de Dados**
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### **6. Configurar Web App**
1. No Dashboard, vá em **"Web"**
2. Clique em **"Add a new web app"**
3. Escolha **"Manual configuration"**
4. Selecione **"Python 3.11"**

### **7. Configurar WSGI**
1. Na aba **"Web"**, clique em **"WSGI configuration file"**
2. Substitua o conteúdo por:

```python
import os
import sys

# Adicionar o projeto ao path
path = '/home/seuusuario/ferramenta_paiol'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'camp_project.settings_prod'

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# Configurar aplicação WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### **8. Configurar Virtualenv**
1. Na aba **"Web"**, em **"Virtualenv"**
2. Digite: `/home/seuusuario/ferramenta_paiol/venv`

### **9. Configurar Static Files**
Na aba **"Web"**, em **"Static files"**:
```
URL: /static/
Directory: /home/seuusuario/ferramenta_paiol/staticfiles/

URL: /media/
Directory: /home/seuusuario/ferramenta_paiol/media/
```

### **10. Reload e Testar**
1. Clique em **"Reload"** (botão verde)
2. Acesse: `https://seuusuario.pythonanywhere.com`

---

## ⚙️ **Configurações Importantes**

### **Estrutura de Diretórios:**
```
/home/seuusuario/
├── ferramenta_paiol/          # Projeto Django
│   ├── venv/                  # Ambiente virtual
│   ├── staticfiles/           # Arquivos estáticos
│   ├── media/                 # Arquivos de mídia
│   ├── .env                   # Variáveis de ambiente
│   └── manage.py
```

### **Comandos de Manutenção:**
```bash
# Ativar ambiente
source ~/ferramenta_paiol/venv/bin/activate
cd ~/ferramenta_paiol

# Atualizar código
git pull origin feature/prod

# Executar migrações
python manage.py migrate

# Coletar static files
python manage.py collectstatic --noinput

# Reload da aplicação (via web interface)
```

---

## 🔧 **Comandos Úteis**

### **Atualizar Aplicação:**
```bash
# No console do PythonAnywhere
cd ~/ferramenta_paiol
source venv/bin/activate

# Puxar atualizações
git pull origin feature/prod

# Instalar novas dependências (se houver)
pip install -r requirements_prod.txt

# Executar migrações
python manage.py migrate

# Coletar static files
python manage.py collectstatic --noinput

# Reload via web interface
```

### **Logs e Debug:**
```bash
# Ver logs de erro
# Dashboard → Web → Error log

# Ver logs de acesso
# Dashboard → Web → Access log

# Console para debug
# Dashboard → Consoles → Bash
```

---

## 🚨 **Solução de Problemas**

### **Erro 500 - Internal Server Error:**
1. Verifique o **Error log** no Dashboard
2. Confirme se `.env` está configurado
3. Verifique se `DJANGO_SETTINGS_MODULE` está correto

### **Static Files não carregam:**
```bash
# Coletar novamente
python manage.py collectstatic --noinput

# Verificar configuração na aba Web
# URL: /static/
# Directory: /home/seuusuario/ferramenta_paiol/staticfiles/
```

### **Erro de Import:**
- Verifique se o virtualenv está configurado corretamente
- Confirme se todas as dependências estão instaladas
- Verifique o path no arquivo WSGI

### **Banco de Dados:**
```bash
# Recriar banco (cuidado - apaga dados!)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 💰 **Custos**
- **Plano Gratuito (Beginner):**
  - 1 web app
  - 512MB de espaço
  - SQLite apenas
  - Domínio: `seuusuario.pythonanywhere.com`
- **Limitações:** CPU limitada, sem HTTPS customizado

---

## 🎉 **Finalização**

Após configuração bem-sucedida:
1. ✅ Acesse `https://seuusuario.pythonanywhere.com`
2. ✅ Teste o login admin
3. ✅ Verifique todas as funcionalidades
4. ✅ Configure tarefas agendadas se necessário

**Seu app estará rodando no PythonAnywhere! 🐍**

---

## 📝 **Dicas Extras**

### **Performance:**
- Use plano pago para PostgreSQL
- Configure cache em arquivo para melhor performance
- Monitore uso de CPU no dashboard

### **Manutenção:**
- Configure tarefas agendadas para limpeza
- Faça backup regular do banco SQLite
- Monitore logs regularmente

### **Upgrade:**
- Considere plano pago para mais recursos
- PostgreSQL disponível em planos pagos
- HTTPS customizado em planos pagos
