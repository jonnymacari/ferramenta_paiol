from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
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
            # cria registro na equipe para gestão da temporada
            from .models import TemporadaEquipe
            TemporadaEquipe.objects.get_or_create(
                temporada=interesse.temporada,
                monitor=interesse.monitor,
                defaults={'status': 'pendente'}
            )
            enviar_email_aprovacao(interesse)

    return redirect('interessados_por_temporada', temporada_id=interesse.temporada.id)

@login_required
@user_passes_test(is_monitor)
def minhas_participacoes(request):
    interesses = InteresseTemporada.objects.filter(
        monitor=request.user,
        status__in=['aprovado', 'confirmado']
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
    if not temporadas:
        messages.info(request, 'Nenhuma temporada selecionada para envio ou já enviada anteriormente.')
        return redirect('lista_temporadas')

    resumo = enviar_email_temporadas_abertas(temporadas)
    messages.success(request, f"E-mails enviados para {resumo['total_monitores']} monitores.")
    for item in resumo['por_temporada']:
        messages.info(request, f"Temporada '{item['nome']}': {item['enviados']} envios.")
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
@user_passes_test(is_gestor)
def configurar_valores(request):
    from .models import ConfiguracaoValores
    instancia = ConfiguracaoValores.objects.order_by('-atualizado_em').first()
    if request.method == 'POST':
        from .forms import ConfiguracaoValoresForm
        form = ConfiguracaoValoresForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Valores de diárias atualizados com sucesso!')
            return redirect('configurar_valores')
        messages.error(request, 'Corrija os erros do formulário de valores.')
    else:
        from .forms import ConfiguracaoValoresForm
        form = ConfiguracaoValoresForm(instance=instancia)
    return render(request, 'configurar_valores.html', {'form': form})


@login_required
@user_passes_test(is_gestor)
def listar_ajudas_custo(request):
    from .models import AjudaCustoClasse
    ajudas = AjudaCustoClasse.objects.all().order_by('nome')
    return render(request, 'listar_ajudas_custo.html', {'ajudas': ajudas})


@login_required
@user_passes_test(is_gestor)
def editar_ajuda_custo(request, ajuda_id=None):
    from .models import AjudaCustoClasse
    ajuda = AjudaCustoClasse.objects.filter(id=ajuda_id).first()
    from .forms import AjudaCustoClasseForm
    if request.method == 'POST':
        form = AjudaCustoClasseForm(request.POST, instance=ajuda)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ajuda de custo salva com sucesso!')
            return redirect('listar_ajudas_custo')
        messages.error(request, 'Corrija os erros do formulário de ajuda de custo.')
    else:
        form = AjudaCustoClasseForm(instance=ajuda)
    return render(request, 'editar_ajuda_custo.html', {'form': form, 'ajuda': ajuda})


def _parse_decimal_br(valor_txt):
    from decimal import Decimal, InvalidOperation
    if not valor_txt:
        return None
    try:
        return Decimal(str(valor_txt).replace(',', '.'))
    except (InvalidOperation, ValueError, TypeError):
        return None


@login_required
@user_passes_test(is_gestor)
def gerenciar_equipe_temporada(request, temporada_id):
    from .models import TemporadaEquipe, AjudaCustoClasse, Temporada
    temporada = get_object_or_404(Temporada, id=temporada_id)
    equipe = TemporadaEquipe.objects.filter(temporada=temporada).select_related('monitor', 'ajuda_custo_classe')
    if request.method == 'POST':
        for membro in equipe:
            prefix = f"m_{membro.id}_"
            membro.recebe_ajuda_custo = bool(request.POST.get(prefix + 'recebe_ajuda_custo'))
            ajuda_id = request.POST.get(prefix + 'ajuda_custo_classe')
            membro.ajuda_custo_classe = AjudaCustoClasse.objects.filter(id=ajuda_id).first() if ajuda_id else None
            membro.recebe_embarque = bool(request.POST.get(prefix + 'recebe_embarque'))
            membro.recebe_desembarque = bool(request.POST.get(prefix + 'recebe_desembarque'))
            membro.valor_embarque_especial = _parse_decimal_br(request.POST.get(prefix + 'valor_embarque_especial'))
            membro.valor_desembarque_especial = _parse_decimal_br(request.POST.get(prefix + 'valor_desembarque_especial'))
            status = request.POST.get(prefix + 'status')
            if status in dict(membro._meta.get_field('status').choices):
                membro.status = status
            membro.save()
        messages.success(request, 'Equipe da temporada atualizada com sucesso!')
        return redirect('gerenciar_equipe_temporada', temporada_id=temporada.id)

    ajudas = AjudaCustoClasse.objects.all()
    return render(request, 'gerenciar_equipe_temporada.html', {
        'temporada': temporada,
        'equipe': equipe,
        'ajudas': ajudas,
    })


@login_required
@user_passes_test(is_monitor)
def relatorio_monitor(request):
    from decimal import Decimal
    from .models import TemporadaEquipe, ConfiguracaoValores
    equipe = TemporadaEquipe.objects.filter(monitor=request.user).select_related('temporada', 'ajuda_custo_classe')
    config = ConfiguracaoValores.objects.order_by('-atualizado_em').first()

    def valor_diaria_para(user, temporada):
        if not config:
            return Decimal('0')
        if temporada.tipo == 'dayuse':
            return config.day_camp
        mapa = {
            'conselheiro_senior': config.conselheiro_senior,
            'conselheiro': config.conselheiro,
            'monitor': config.monitor,
            'monitor_junior': config.monitor_junior,
            'estagiario': config.estagiario,
            'enfermeira': config.enfermeira,
            'enfermeira_estagiaria': config.enfermeira_estagiaria,
            'fotografo_1': config.fotografo_1,
            'fotografo_2': config.fotografo_2,
        }
        return mapa.get(user.categoria, Decimal('0')) or Decimal('0')

    itens = []
    for m in equipe:
        diaria = valor_diaria_para(request.user, m.temporada)
        diarias = m.temporada.numero_diarias or 0
        ajuda = m.ajuda_custo_classe.valor if (m.recebe_ajuda_custo and m.ajuda_custo_classe) else 0
        embarque = m.valor_embarque_especial or 0
        desembarque = m.valor_desembarque_especial or 0
        total = (diaria * diarias) + ajuda + embarque + desembarque
        itens.append({
            'temporada': m.temporada,
            'funcao': getattr(request.user, 'get_categoria_display', lambda: request.user.categoria)(),
            'valor_diaria': diaria,
            'numero_diarias': diarias,
            'ajuda': ajuda,
            'embarque': embarque,
            'desembarque': desembarque,
            'status': m.get_status_display(),
            'total': total,
        })

    return render(request, 'relatorio_monitor.html', {'itens': itens})

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
