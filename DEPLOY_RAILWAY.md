# 🚀 Deploy no Railway - Ferramenta Paiol

## 📋 **Pré-requisitos**
- Conta no [Railway](https://railway.app)
- Conta no GitHub
- Projeto na branch `feature/prod`

---

## 🎯 **Passo a Passo - Railway**

### **1. Preparar o Repositório**
```bash
# Certifique-se de estar na branch correta
git checkout feature/prod

# Commit todas as mudanças
git add .
git commit -m "Configuração para produção"
git push origin feature/prod
```

### **2. Criar Projeto no Railway**
1. Acesse [railway.app](https://railway.app)
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha seu repositório `ferramenta_paiol`
5. Selecione a branch `feature/prod`

### **3. Configurar Variáveis de Ambiente**
No painel do Railway, vá em **Variables** e adicione:

```env
# Obrigatórias
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
DJANGO_SETTINGS_MODULE=camp_project.settings_prod
HOSTING_PROVIDER=railway

# Opcionais (se quiser usar PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Email (se configurado)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### **4. Configurar Banco de Dados (Opcional)**
Para usar PostgreSQL (recomendado):
1. No Railway, clique em **"New"** → **"Database"** → **"PostgreSQL"**
2. Copie a `DATABASE_URL` gerada
3. Cole nas variáveis de ambiente

### **5. Deploy Automático**
- O Railway detectará automaticamente o `Procfile`
- O deploy iniciará automaticamente
- Aguarde a conclusão (pode levar alguns minutos)

### **6. Configurar Domínio**
1. No painel do projeto, vá em **"Settings"**
2. Em **"Domains"**, clique em **"Generate Domain"**
3. Seu app estará disponível em: `https://seu-app.up.railway.app`

---

## ⚙️ **Configurações Importantes**

### **Arquivos Utilizados:**
- ✅ `Procfile` - Comandos de inicialização
- ✅ `railway.json` - Configurações específicas
- ✅ `requirements_prod.txt` - Dependências
- ✅ `runtime.txt` - Versão do Python

### **Comandos Executados Automaticamente:**
```bash
# Instalar dependências
pip install -r requirements_prod.txt

# Executar migrações (via Procfile)
python manage.py migrate

# Iniciar servidor
gunicorn camp_project.wsgi --log-file -
```

---

## 🔧 **Comandos Úteis**

### **Executar Comandos no Railway:**
```bash
# Acessar console do Railway
railway shell

# Executar migrações manualmente
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

---

## 🚨 **Solução de Problemas**

### **Erro de Static Files:**
```bash
# No console do Railway
python manage.py collectstatic --noinput
```

### **Erro de Migração:**
```bash
# No console do Railway
python manage.py migrate --run-syncdb
```

### **Erro de Variáveis:**
- Verifique se todas as variáveis obrigatórias estão configuradas
- `SECRET_KEY` deve ser uma string longa e aleatória
- `DEBUG` deve ser `False`

---

## 💰 **Custos**
- **Plano Gratuito:** $5 de crédito mensal
- **Uso típico:** ~$3-5/mês para aplicação pequena
- **PostgreSQL:** Incluído no plano

---

## 🎉 **Finalização**

Após o deploy bem-sucedido:
1. ✅ Acesse seu domínio Railway
2. ✅ Teste o login admin
3. ✅ Verifique todas as funcionalidades
4. ✅ Configure email se necessário

**Seu app estará rodando em produção! 🚀**
