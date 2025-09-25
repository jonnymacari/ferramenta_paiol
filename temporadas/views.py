from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from .forms import TemporadaForm
from .models import Temporada, InteresseTemporada
from django.utils import timezone
from .utils import enviar_email_aprovacao, enviar_email_temporadas_abertas, is_gestor, is_monitor
from datetime import timedelta
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404


def is_gestor(user):
    return user.is_authenticated and user.user_type == 'gestor'

@login_required
@user_passes_test(is_gestor)
def criar_temporada(request):
    if request.method == 'POST':
        form = TemporadaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_temporadas')
    else:
        form = TemporadaForm()
    return render(request, 'criar_temporada.html', {'form': form})

@login_required
@user_passes_test(is_gestor)
def listar_temporadas(request):
    temporadas = Temporada.objects.all().order_by('data_inicio')
    return render(request, 'lista_temporadas.html', {'temporadas': temporadas})

@login_required
@user_passes_test(lambda u: u.user_type == 'monitor' and u.is_approved)
def listar_temporadas_monitor(request):
    hoje = timezone.now().date()
    temporadas_disponiveis = Temporada.objects.filter(data_fim__gte=hoje).exclude(
        interessetemporada__monitor=request.user
    )
    return render(request, 'lista_temporadas_monitor.html', {
        'temporadas': temporadas_disponiveis
    })

@login_required
@user_passes_test(lambda u: u.user_type == 'monitor' and u.is_approved)
def demonstrar_interesse(request, temporada_id):
    temporada = Temporada.objects.get(id=temporada_id)
    interesse, created = InteresseTemporada.objects.get_or_create(
        monitor=request.user,
        temporada=temporada,
        defaults={'status': 'interessado'}
    )
    return redirect('listar_temporadas_monitor')

@login_required
@user_passes_test(is_gestor)
def interessados_por_temporada(request, temporada_id):
    temporada = Temporada.objects.get(id=temporada_id)
    interessados = InteresseTemporada.objects.filter(temporada=temporada)

    return render(request, 'interessados_por_temporada.html', {
        'temporada': temporada,
        'interessados': interessados
    })

@require_POST
@login_required
@user_passes_test(is_gestor)
def alterar_status_interesse(request, interesse_id):
    interesse = InteresseTemporada.objects.get(id=interesse_id)
    novo_status = request.POST.get('status')

    if novo_status in ['aprovado', 'recusado']:
        interesse.status = novo_status
        interesse.save()
        if novo_status == 'aprovado':
            enviar_email_aprovacao(interesse)

    return redirect('interessados_por_temporada', temporada_id=interesse.temporada.id)

@login_required
@user_passes_test(is_monitor)
def minhas_participacoes(request):
    interesses = InteresseTemporada.objects.filter(
        monitor=request.user,
        status='confirmado'
    )
    temporadas = [i.temporada for i in interesses]

    return render(request, 'minhas_participacoes.html', {
        'temporadas': temporadas
    })


@require_POST
@login_required
@user_passes_test(lambda u: u.user_type == 'monitor')
def resposta_participacao(request, interesse_id):
    interesse = InteresseTemporada.objects.get(id=interesse_id, monitor=request.user)
    acao = request.POST.get('acao')

    if interesse.status == 'aprovado':
        if acao == 'confirmar':
            interesse.status = 'confirmado'
        elif acao == 'recusar':
            interesse.status = 'recusado'
        interesse.save()
    
    return redirect('minhas_participacoes')

@require_POST
@login_required
@user_passes_test(is_gestor)
def enviar_emails_temporadas(request):
    ids = request.POST.getlist('temporadas')
    temporadas = Temporada.objects.filter(id__in=ids, email_enviado=False)
    enviar_email_temporadas_abertas(temporadas)
    return redirect('lista_temporadas')

@login_required
@require_POST
@user_passes_test(is_gestor)
def habilitar_reenvio_email(request, temporada_id):
    """View para habilitar o reenvio de email para uma temporada específica"""
    try:
        temporada = get_object_or_404(Temporada, id=temporada_id)
        temporada.email_enviado = False
        temporada.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Reenvio de email habilitado com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Erro ao habilitar reenvio: {str(e)}'
        })

@login_required
def api_temporadas_json(request):
    if request.user.user_type == 'gestor':
        temporadas = Temporada.objects.all()
    else:
        temporadas_ids = InteresseTemporada.objects.filter(
            monitor=request.user,
            status='confirmado'
        ).values_list('temporada', flat=True)
        temporadas = Temporada.objects.filter(id__in=temporadas_ids)

    cores = [
        {"bg": "#0865AF", "border": "#054a7e"},
        {"bg": "#FEBD02", "border": "#d4a901"},
        {"bg": "#28a745", "border": "#1e7e34"},
        {"bg": "#dc3545", "border": "#a71d2a"},
        {"bg": "#6f42c1", "border": "#5936a2"},
        {"bg": "#20c997", "border": "#159b7e"},
    ]

    eventos = []
    for idx, t in enumerate(temporadas):
        cor = cores[idx % len(cores)]  # troca as cores ciclicamente
        eventos.append({
            "id": t.id,
            "title": t.nome,
            "start": t.data_inicio.isoformat(),
            "end": (t.data_fim + timedelta(days=1)).isoformat(),
            "backgroundColor": cor["bg"],
            "borderColor": cor["border"],
            "extendedProps": {
                "cliente": t.cliente,
                "tipo": t.get_tipo_display(),
                "data_inicio": t.data_inicio.strftime('%d/%m/%Y'),
                "data_fim": t.data_fim.strftime('%d/%m/%Y')
            }
        })


    return JsonResponse(eventos, safe=False)

@login_required
def calendario_novo_view(request):
    return render(request, 'calendario_full.html')

@login_required
@user_passes_test(is_gestor)
def detalhes_temporada(request, temporada_id):
    temporada = get_object_or_404(Temporada, id=temporada_id)

    if request.method == 'POST':
        form = TemporadaForm(request.POST, instance=temporada)
        if form.is_valid():
            form.save()
            return redirect('lista_temporadas')
    else:
        form = TemporadaForm(instance=temporada)

    return render(request, 'detalhes_temporada.html', {
        'temporada': temporada,
        'form': form
    })

@login_required
@user_passes_test(is_monitor)
def visualizar_temporada_monitor(request, temporada_id):
    temporada = get_object_or_404(Temporada, id=temporada_id)

    # Futuro: incluir outras infos como documentos, status etc.
    return render(request, 'visualizar_temporada_monitor.html', {
        'temporada': temporada
    })

@login_required
def api_temporadas_json(request):
    if request.user.user_type == 'gestor':
        temporadas = Temporada.objects.all()
    else:
        temporadas_ids = InteresseTemporada.objects.filter(
            monitor=request.user,
            status='confirmado'
        ).values_list('temporada', flat=True)
        temporadas = Temporada.objects.filter(id__in=temporadas_ids)

    cores = [
        {"bg": "#0865AF", "border": "#054a7e"},
        {"bg": "#FEBD02", "border": "#d4a901"},
        {"bg": "#28a745", "border": "#1e7e34"},
        {"bg": "#dc3545", "border": "#a71d2a"},
        {"bg": "#6f42c1", "border": "#5936a2"},
        {"bg": "#20c997", "border": "#159b7e"},
    ]

    eventos = []
    for idx, t in enumerate(temporadas):
        cor = cores[idx % len(cores)]  # troca as cores ciclicamente
        eventos.append({
            "id": t.id,
            "title": t.nome,
            "start": t.data_inicio.isoformat(),
            "end": (t.data_fim + timedelta(days=1)).isoformat(),
            "backgroundColor": cor["bg"],
            "borderColor": cor["border"],
            "extendedProps": {
                "cliente": t.cliente,
                "tipo": t.get_tipo_display(),
                "data_inicio": t.data_inicio.strftime('%d/%m/%Y'),
                "data_fim": t.data_fim.strftime('%d/%m/%Y')
            }
        })


    return JsonResponse(eventos, safe=False)

@login_required
def calendario_novo_view(request):
    return render(request, 'calendario_full.html')

@login_required
@user_passes_test(is_gestor)
def detalhes_temporada(request, temporada_id):
    temporada = get_object_or_404(Temporada, id=temporada_id)

    if request.method == 'POST':
        form = TemporadaForm(request.POST, instance=temporada)
        if form.is_valid():
            form.save()
            return redirect('lista_temporadas')
    else:
        form = TemporadaForm(instance=temporada)

    return render(request, 'detalhes_temporada.html', {
        'temporada': temporada,
        'form': form
    })

@login_required
@user_passes_test(is_monitor)
def visualizar_temporada_monitor(request, temporada_id):
    temporada = get_object_or_404(Temporada, id=temporada_id)

    # Futuro: incluir outras infos como documentos, status etc.
    return render(request, 'visualizar_temporada_monitor.html', {
        'temporada': temporada
    })
