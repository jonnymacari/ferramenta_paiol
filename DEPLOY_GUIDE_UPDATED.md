# 🚀 Guia de Deploy Atualizado - Ferramenta Paiol

## 📋 **Visão Geral**

Este projeto está configurado para deploy em múltiplas plataformas de hospedagem gratuita. Escolha a opção que melhor se adequa às suas necessidades.

---

## 🏆 **Opções de Hospedagem Recomendadas**

### **1. 🚄 Railway (Mais Recomendado)**
- ✅ **Deploy automático** via GitHub
- ✅ **PostgreSQL gratuito** incluído
- ✅ **SSL automático**
- ✅ **Domínio personalizado** fácil
- ✅ **$5 de crédito mensal** (suficiente para apps pequenos)
- ⚠️ **Pago após créditos** (~$3-5/mês)

**👉 [Ver guia completo: DEPLOY_RAILWAY.md](./DEPLOY_RAILWAY.md)**

### **2. 🌐 Render**
- ✅ **750 horas gratuitas/mês**
- ✅ **PostgreSQL gratuito** (90 dias)
- ✅ **SSL automático**
- ✅ **Build automático**
- ⚠️ **App "dorme"** após 15min inativo
- ⚠️ **PostgreSQL pago** após período gratuito

**👉 [Ver guia completo: DEPLOY_RENDER.md](./DEPLOY_RENDER.md)**

### **3. 🐍 PythonAnywhere**
- ✅ **Completamente gratuito**
- ✅ **Especializado em Python**
- ✅ **Console SSH** incluído
- ⚠️ **Apenas SQLite** no plano gratuito
- ⚠️ **Setup manual** necessário
- ⚠️ **CPU limitada**

**👉 [Ver guia completo: DEPLOY_PYTHONANYWHERE.md](./DEPLOY_PYTHONANYWHERE.md)**

---

## 🎯 **Comparação Rápida**

| Característica | Railway | Render | PythonAnywhere |
|----------------|---------|--------|----------------|
| **Custo** | $3-5/mês | Gratuito* | Gratuito |
| **PostgreSQL** | ✅ Incluído | ✅ 90 dias | ❌ SQLite apenas |
| **SSL** | ✅ Automático | ✅ Automático | ❌ Não |
| **Deploy** | ✅ Automático | ✅ Automático | ⚠️ Manual |
| **Domínio** | ✅ Fácil | ✅ Fácil | ⚠️ Subdomínio |
| **Performance** | ✅ Excelente | ⚠️ Dorme | ⚠️ Limitada |
| **Facilidade** | ✅ Muito fácil | ✅ Fácil | ⚠️ Intermediário |

*Render: PostgreSQL pago após 90 dias

---

## 📁 **Arquivos de Configuração**

O projeto inclui todos os arquivos necessários para deploy:

### **Para Railway:**
- ✅ `Procfile` - Comandos de inicialização
- ✅ `railway.json` - Configurações específicas
- ✅ `requirements_prod.txt` - Dependências

### **Para Render:**
- ✅ `render.yaml` - Configuração completa
- ✅ `build.sh` - Script de build
- ✅ `requirements_prod.txt` - Dependências

### **Para PythonAnywhere:**
- ✅ `settings_prod.py` - Configurações de produção
- ✅ `manage_prod.py` - Gerenciador para produção
- ✅ `requirements_prod.txt` - Dependências

### **Gerais:**
- ✅ `.env.example` - Template de variáveis
- ✅ `runtime.txt` - Versão do Python
- ✅ `.gitignore` - Arquivos ignorados

---

## ⚙️ **Configuração Inicial**

### **1. Preparar Branch de Produção**
```bash
# Certifique-se de estar na branch correta
git checkout feature/prod

# Verificar arquivos de configuração
ls -la | grep -E "(Procfile|build.sh|railway.json|render.yaml)"
```

### **2. Configurar Variáveis de Ambiente**
Copie `.env.example` para `.env` e configure:
```bash
cp .env.example .env
nano .env
```

**Variáveis obrigatórias:**
```env
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
DJANGO_SETTINGS_MODULE=camp_project.settings_prod
```

### **3. Testar Localmente (Opcional)**
```bash
# Instalar dependências de produção
pip install -r requirements_prod.txt

# Testar configurações
python manage_prod.py check --deploy

# Coletar arquivos estáticos
python manage_prod.py collectstatic --noinput
```

---

## 🚨 **Solução de Problemas Comuns**

### **Erro de Static Files:**
```bash
python manage.py collectstatic --noinput
```

### **Erro de Migração:**
```bash
python manage.py migrate --run-syncdb
```

### **Erro de SECRET_KEY:**
- Gere uma nova chave: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Configure nas variáveis de ambiente

### **Erro de ALLOWED_HOSTS:**
- Adicione seu domínio em `settings_prod.py`
- Ou configure via variável `ALLOWED_HOST`

---

## 🎉 **Próximos Passos**

Após escolher sua plataforma:

1. **Siga o guia específico** da plataforma escolhida
2. **Configure as variáveis** de ambiente
3. **Faça o deploy** seguindo as instruções
4. **Teste todas as funcionalidades**
5. **Configure domínio personalizado** (se necessário)

---

## 📞 **Suporte**

Se encontrar problemas:
1. Consulte os logs da plataforma
2. Verifique as variáveis de ambiente
3. Confirme se todos os arquivos estão commitados
4. Teste localmente primeiro

**Boa sorte com seu deploy! 🚀**
