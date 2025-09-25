# 🌐 Deploy no Render - Ferramenta Paiol

## 📋 **Pré-requisitos**
- Conta no [Render](https://render.com)
- Conta no GitHub
- Projeto na branch `feature/prod`

---

## 🎯 **Passo a Passo - Render**

### **1. Preparar o Repositório**
```bash
# Certifique-se de estar na branch correta
git checkout feature/prod

# Commit todas as mudanças
git add .
git commit -m "Configuração para produção"
git push origin feature/prod
```

### **2. Criar Web Service no Render**
1. Acesse [render.com](https://render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Selecione `ferramenta_paiol`
5. Escolha a branch `feature/prod`

### **3. Configurar o Web Service**
```yaml
# Configurações básicas
Name: ferramenta-paiol
Environment: Python 3
Region: Oregon (US West)
Branch: feature/prod

# Comandos de build e start
Build Command: ./build.sh
Start Command: gunicorn camp_project.wsgi:application
```

### **4. Configurar Variáveis de Ambiente**
Na seção **Environment**, adicione:

```env
# Obrigatórias
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
DJANGO_SETTINGS_MODULE=camp_project.settings_prod
HOSTING_PROVIDER=render

# Será configurado automaticamente se usar PostgreSQL do Render
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### **5. Configurar Banco de Dados PostgreSQL**
1. Clique em **"New +"** → **"PostgreSQL"**
2. Configure:
   ```yaml
   Name: ferramenta-paiol-db
   Database: ferramenta_paiol
   User: ferramenta_paiol_user
   ```
3. Após criado, copie a **Internal Database URL**
4. Cole como `DATABASE_URL` no Web Service

### **6. Deploy**
1. Clique em **"Create Web Service"**
2. O Render executará automaticamente:
   ```bash
   ./build.sh  # Instala deps, coleta static, migra
   gunicorn camp_project.wsgi:application
   ```
3. Aguarde a conclusão (5-10 minutos)

### **7. Configurar Domínio**
- Seu app estará disponível em: `https://ferramenta-paiol.onrender.com`
- Para domínio customizado, vá em **Settings** → **Custom Domains**

---

## ⚙️ **Configurações Importantes**

### **Arquivos Utilizados:**
- ✅ `render.yaml` - Configuração completa (opcional)
- ✅ `build.sh` - Script de build
- ✅ `requirements_prod.txt` - Dependências
- ✅ `runtime.txt` - Versão do Python

### **Script de Build (`build.sh`):**
```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements_prod.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

---

## 🔧 **Comandos Úteis**

### **Logs e Debug:**
```bash
# Ver logs em tempo real
# No painel do Render → Logs

# Executar comandos via shell (não disponível no plano gratuito)
# Usar apenas via deploy
```

### **Redeploy Manual:**
1. No painel do Render
2. Clique em **"Manual Deploy"**
3. Selecione **"Deploy latest commit"**

---

## 🚨 **Solução de Problemas**

### **Erro de Build:**
- Verifique se `build.sh` tem permissão de execução
- Confirme se `requirements_prod.txt` existe
- Veja os logs de build no painel

### **Erro de Static Files:**
```bash
# No build.sh, certifique-se de ter:
python manage.py collectstatic --no-input
```

### **Erro de Database:**
- Verifique se `DATABASE_URL` está configurada
- Confirme se o PostgreSQL está rodando
- Teste a conexão no painel do banco

### **Erro de Variáveis:**
- `SECRET_KEY` deve ser definida manualmente
- `DEBUG=False` é obrigatório
- Verifique todas as variáveis na seção Environment

---

## 💰 **Custos**
- **Plano Gratuito:** 
  - 750 horas/mês de Web Service
  - PostgreSQL gratuito (90 dias, depois $7/mês)
  - SSL automático
- **Limitações:** App "dorme" após 15min de inatividade

---

## 🎉 **Finalização**

Após o deploy bem-sucedido:
1. ✅ Acesse `https://seu-app.onrender.com`
2. ✅ Teste o login admin
3. ✅ Verifique todas as funcionalidades
4. ✅ Configure domínio customizado se necessário

**Seu app estará rodando em produção com SSL automático! 🌐**

---

## 📝 **Dicas Extras**

### **Performance:**
- Use PostgreSQL em vez de SQLite
- Configure Redis para cache (plano pago)
- Monitore uso de recursos no painel

### **Segurança:**
- SSL é automático no Render
- Configure `ALLOWED_HOSTS` corretamente
- Use variáveis de ambiente para dados sensíveis
