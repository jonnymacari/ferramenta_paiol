from django.core.mail import send_mail
from django.conf import settings
from core.models import CustomUser
import logging

logger = logging.getLogger(__name__)

def enviar_email_temporadas_abertas(temporadas):
    """Envia email para monitores aprovados sobre novas temporadas"""
    try:
        # Filtrar apenas monitores aprovados e com email
        monitores = CustomUser.objects.filter(
            user_type='monitor', 
            is_approved=True
        ).exclude(email='').distinct()
        
        if not monitores.exists():
            logger.warning("Nenhum monitor aprovado encontrado para envio de email")
            return False
            
        destinatarios = [monitor.email for monitor in monitores]
        emails_enviados = 0

        for temporada in temporadas:
            try:
                # Criar nome da temporada baseado no tipo e cliente
                nome_temporada = f"{temporada.get_tipo_display()}"
                if temporada.cliente:
                    nome_temporada += f" - {temporada.cliente}"
                    
                assunto = f"Nova temporada disponível: {nome_temporada}"
                mensagem = f"""
Olá! Uma nova temporada foi aberta:

Tipo: {temporada.get_tipo_display()}
Cliente: {temporada.cliente or 'Não informado'}
Data: {temporada.data_inicio.strftime('%d/%m/%Y')} a {temporada.data_fim.strftime('%d/%m/%Y')}
Diárias: {temporada.numero_diarias}

Acesse o sistema para demonstrar interesse.

Equipe do Acampamento.
"""
                send_mail(
                    assunto,
                    mensagem,
                    settings.DEFAULT_FROM_EMAIL,
                    destinatarios,
                    fail_silently=False
                )
                temporada.email_enviado = True
                temporada.save()
                emails_enviados += 1
                logger.info(f"Email enviado com sucesso para temporada {temporada.id}")
                
            except Exception as e:
                logger.error(f"Erro ao enviar email para temporada {temporada.id}: {str(e)}")
                continue
                
        return emails_enviados > 0
        
    except Exception as e:
        logger.error(f"Erro geral no envio de emails: {str(e)}")
        return False

def enviar_email_aprovacao(interesse):
    """Envia email de aprovação para monitor"""
    try:
        if not interesse.monitor.email:
            logger.warning(f"Monitor {interesse.monitor.username} não tem email cadastrado")
            return False
            
        # Criar nome da temporada
        nome_temporada = f"{interesse.temporada.get_tipo_display()}"
        if interesse.temporada.cliente:
            nome_temporada += f" - {interesse.temporada.cliente}"
            
        send_mail(
            f"Você foi aprovado para: {nome_temporada}",
            f"""
Parabéns! Você foi aprovado para participar da temporada: {nome_temporada}

Data: {interesse.temporada.data_inicio.strftime('%d/%m/%Y')} a {interesse.temporada.data_fim.strftime('%d/%m/%Y')}
Diárias: {interesse.temporada.numero_diarias}

Por favor, acesse sua conta para confirmar ou recusar a participação.

Equipe do Acampamento.
""",
            settings.DEFAULT_FROM_EMAIL,
            [interesse.monitor.email],
            fail_silently=False
        )
        logger.info(f"Email de aprovação enviado para {interesse.monitor.email}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de aprovação: {str(e)}")
        return False

def is_gestor(user):
    return user.is_authenticated and user.user_type == 'gestor'

def is_monitor(user):
    return user.is_authenticated and user.user_type == 'monitor'
