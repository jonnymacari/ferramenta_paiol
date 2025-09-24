from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CompleteProfileForm, UserManagementForm, CSVUploadForm
from temporadas.models import Temporada, InteresseTemporada
from temporadas.utils import is_gestor, is_monitor
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CustomUser


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
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Validar se os campos foram preenchidos
        if not username_or_email:
            messages.error(request, 'Por favor, digite seu nome de usuário ou e-mail.')
            return render(request, 'login.html')
        
        if not password:
            messages.error(request, 'Por favor, digite sua senha.')
            return render(request, 'login.html')
        
        # Tentar autenticar com username
        user = authenticate(request, username=username_or_email, password=password)
        
        # Se não funcionou, tentar com email
        if not user:
            try:
                # Buscar usuário pelo email
                user_by_email = CustomUser.objects.get(email=username_or_email)
                user = authenticate(request, username=user_by_email.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Bem-vindo(a), {user.first_name or user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Sua conta está desativada. Entre em contato com o administrador.')
        else:
            messages.error(request, 'Nome de usuário/e-mail ou senha incorretos. Verifique suas credenciais e tente novamente.')
    
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



# Views de gerenciamento de usuários para gestores

@login_required
@user_passes_test(is_gestor)
def manage_users(request):
    """Lista todos os usuários com paginação e busca"""
    search_query = request.GET.get('search', '')
    user_type_filter = request.GET.get('user_type', '')
    
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Aplicar filtros
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)
    
    # Paginação
    paginator = Paginator(users, 20)  # 20 usuários por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
        'user_types': CustomUser._meta.get_field('user_type').choices,
    }
    
    return render(request, 'manage_users.html', context)


@login_required
@user_passes_test(is_gestor)
def create_user(request):
    """Criar novo usuário"""
    if request.method == 'POST':
        form = UserManagementForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuário "{user.username}" criado com sucesso!')
            return redirect('manage_users')
    else:
        form = UserManagementForm()
    
    return render(request, 'create_user.html', {'form': form})


@login_required
@user_passes_test(is_gestor)
def edit_user(request, user_id):
    """Editar usuário existente"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=user, is_edit=True)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuário "{user.username}" atualizado com sucesso!')
            return redirect('manage_users')
    else:
        form = UserManagementForm(instance=user, is_edit=True)
    
    return render(request, 'edit_user.html', {'form': form, 'user_obj': user})


@login_required
@user_passes_test(is_gestor)
def delete_user(request, user_id):
    """Deletar usuário"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Não permitir deletar o próprio usuário
    if user == request.user:
        messages.error(request, 'Você não pode deletar sua própria conta!')
        return redirect('manage_users')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuário "{username}" deletado com sucesso!')
        return redirect('manage_users')
    
    return render(request, 'delete_user.html', {'user_obj': user})


@login_required
@user_passes_test(is_gestor)
def bulk_create_users(request):
    """Criar usuários em lote via CSV"""
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                users_to_create, errors = form.process_csv()
                
                if errors:
                    for error in errors:
                        messages.error(request, error)
                    return render(request, 'bulk_create_users.html', {'form': form})
                
                # Criar usuários
                created_users = []
                for user_data in users_to_create:
                    password = user_data.pop('password')
                    user = CustomUser(**user_data)
                    user.set_password(password)
                    user.save()
                    created_users.append(user)
                
                messages.success(
                    request, 
                    f'{len(created_users)} usuário(s) criado(s) com sucesso!'
                )
                return redirect('manage_users')
                
            except Exception as e:
                messages.error(request, f'Erro ao processar arquivo CSV: {str(e)}')
    else:
        form = CSVUploadForm()
    
    return render(request, 'bulk_create_users.html', {'form': form})


@login_required
@user_passes_test(is_gestor)
def user_detail(request, user_id):
    """Ver detalhes de um usuário"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Buscar informações adicionais se for monitor
    temporadas_info = None
    if user.user_type == 'monitor':
        temporadas_info = {
            'participacoes': InteresseTemporada.objects.filter(monitor=user, status='confirmado').count(),
            'pendentes': InteresseTemporada.objects.filter(monitor=user, status='pendente').count(),
        }
    
    context = {
        'user_obj': user,
        'temporadas_info': temporadas_info,
    }
    
    return render(request, 'user_detail.html', context)

