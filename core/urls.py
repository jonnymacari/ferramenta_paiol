from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_home, name='public_home'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    
    # URLs de gerenciamento de usuários
    path('manage-users/', views.manage_users, name='manage_users'),
    path('create-user/', views.create_user, name='create_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user-detail/<int:user_id>/', views.user_detail, name='user_detail'),
    path('bulk-create-users/', views.bulk_create_users, name='bulk_create_users'),
    
    # Dashboard BI
    path('bi-dashboard/', views.bi_dashboard, name='bi_dashboard'),
    
    # Aprovação de monitores
    path('approve-monitors/', views.approve_monitors, name='approve_monitors'),
    path('approve-monitor/<int:monitor_id>/', views.approve_monitor, name='approve_monitor'),
]
