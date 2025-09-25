from django.urls import path
from . import views

urlpatterns = [
    path('criar/', views.criar_temporada, name='criar_temporada'),
    path('listar/', views.listar_temporadas, name='lista_temporadas'),
    path('disponiveis/', views.listar_temporadas_monitor, name='listar_temporadas_monitor'),
    path('interesse/<int:temporada_id>/', views.demonstrar_interesse, name='demonstrar_interesse'),
    path('<int:temporada_id>/interessados/', views.interessados_por_temporada, name='interessados_por_temporada'),
    path('interesse/<int:interesse_id>/alterar/', views.alterar_status_interesse, name='alterar_status_interesse'),
    path('minhas/', views.minhas_participacoes, name='minhas_participacoes'),
    path('responder/<int:interesse_id>/', views.resposta_participacao, name='resposta_participacao'),
    path('enviar_emails/', views.enviar_emails_temporadas, name='enviar_emails_temporadas'),
    path('<int:temporada_id>/habilitar_reenvio/', views.habilitar_reenvio_email, name='habilitar_reenvio_email'),
    path('calendario/', views.calendario_novo_view, name='calendario'),
    path('api/temporadas/', views.api_temporadas_json, name='api_temporadas_json'),
    path('<int:temporada_id>/', views.detalhes_temporada, name='detalhes_temporada'),
    path('<int:temporada_id>/visualizar/', views.visualizar_temporada_monitor, name='visualizar_temporada_monitor'),
]
