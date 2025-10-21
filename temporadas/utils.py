from django.core.mail import send_mail
from core.models import CustomUser


def enviar_email_temporadas_abertas(temporadas):
    """Envia e-mails e retorna um resumo do envio."""
    monitores = CustomUser.objects.filter(user_type='monitor').exclude(email='').distinct()
    destinatarios = [m.email for m in monitores]

    resumo = {
        'total_monitores': len(destinatarios),
        'por_temporada': []
    }

    for temporada in temporadas:
        assunto = f"Nova temporada disponível: {temporada.nome}"
        mensagem = f"""
Olá! Uma nova temporada foi aberta:

Nome: {temporada.nome}
Data: {temporada.data_inicio} a {temporada.data_fim}
Cliente: {temporada.cliente or '-'}
Tipo: {temporada.get_tipo_display()}

Acesse o sistema para demonstrar interesse.

Equipe do Acampamento.
"""
        send_mail(
            assunto,
            mensagem,
            None,
            destinatarios,
            fail_silently=False
        )
        temporada.email_enviado = True
        temporada.save()
        resumo['por_temporada'].append({
            'id': temporada.id,
            'nome': temporada.nome,
            'enviados': len(destinatarios),
        })

    return resumo


def enviar_email_aprovacao(interesse):
    send_mail(
        f"Você foi aprovado para: {interesse.temporada.nome}",
        f"""
Parabéns! Você foi aprovado para participar da temporada: {interesse.temporada.nome}

Data: {interesse.temporada.data_inicio} a {interesse.temporada.data_fim}

Por favor, acesse sua conta para confirmar ou recusar a participação.

Equipe do Acampamento.
""",
        None,
        [interesse.monitor.email],
        fail_silently=False
    )


def is_gestor(user):
    return user.is_authenticated and user.user_type == 'gestor'


def is_monitor(user):
    return user.is_authenticated and user.user_type == 'monitor'

