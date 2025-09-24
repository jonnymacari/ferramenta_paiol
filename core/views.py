from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CompleteProfileForm
from temporadas.models import Temporada, InteresseTemporada
from temporadas.utils import is_gestor, is_monitor
from django.contrib import messages


def public_home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    if request.user.user_type == 'admin':
        return render(request, 'home_admin.html')

    elif request.user.user_type == 'gestor':
        # Encaminha para a view com dados dinâmicos
        return home_gestor(request)

    elif request.user.user_type == 'monitor':
        return home_monitor(request)

    return redirect('login')


@login_required
@user_passes_test(is_gestor)
def home_gestor(request):
    from .models import CustomUser
    
    total_temporadas = Temporada.objects.count()
    interesses_pendentes = InteresseTemporada.objects.filter(status='pendente').count()
    temporadas_sem_email = Temporada.objects.filter(email_enviado=False).count()
    
    # Informações de todos os usuários para o dashboard do gestor
    total_usuarios = CustomUser.objects.count()
    usuarios_por_tipo = {
        'admin': CustomUser.objects.filter(user_type='admin').count(),
        'gestor': CustomUser.objects.filter(user_type='gestor').count(),
        'monitor': CustomUser.objects.filter(user_type='monitor').count(),
    }
    
    # Últimos usuários cadastrados
    ultimos_usuarios = CustomUser.objects.order_by('-date_joined')[:5]

    return render(request, 'home_gestor.html', {
        'total_temporadas': total_temporadas,
        'interesses_pendentes': interesses_pendentes,
        'temporadas_sem_email': temporadas_sem_email,
        'total_usuarios': total_usuarios,
        'usuarios_por_tipo': usuarios_por_tipo,
        'ultimos_usuarios': ultimos_usuarios,
    })


@login_required
@user_passes_test(is_monitor)
def home_monitor(request):
    from temporadas.models import Temporada, InteresseTemporada

    # IDs das temporadas que o monitor já se envolveu (interesse ou confirmação)
    temporadas_relacionadas = InteresseTemporada.objects.filter(
        monitor=request.user
    ).values_list('temporada_id', flat=True)

    # Temporadas enviadas por email, mas que o monitor ainda não demonstrou interesse
    temporadas_disponiveis = Temporada.objects.filter(
        email_enviado=True
    ).exclude(id__in=temporadas_relacionadas).count()

    minhas_temporadas = InteresseTemporada.objects.filter(
        monitor=request.user,
        status='confirmado'
    ).count()

    return render(request, 'home_monitor.html', {
        'temporadas_disponiveis': temporadas_disponiveis,
        'minhas_temporadas': minhas_temporadas
    })


@login_required
@user_passes_test(is_monitor)
def complete_profile(request):
    """View para completar o perfil do monitor"""
    if request.method == 'POST':
        form = CompleteProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('home')
    else:
        form = CompleteProfileForm(instance=request.user)
    
    return render(request, 'complete_profile.html', {'form': form})
