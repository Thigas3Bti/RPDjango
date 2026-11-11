from django.urls import path

from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('inicio/', views.inicio, name='inicio'),
    path('equipamentos/', views.equipamentos, name='equipamentos'),
    path(
        'equipamentos/<int:equipamento_id>/',
        views.detalhe_equipamento,
        name='detalhe_equipamento',
    ),
    path('equipamentos/cadastrar/', views.cadastrar_equipamento, name='cadastrar_equipamento'),
    path('contato/', views.contato, name='contato'),
    path('mensagens/', views.mensagens_contato, name='mensagens_contato'),
    path(
        'mensagens/<int:mensagem_id>/status/',
        views.atualizar_status_mensagem,
        name='atualizar_status_mensagem',
    ),
    path('surpresa/', views.surpresa, name='surpresa'),
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path(
        'mensagens/solicitacoes-senha/',
        views.gerenciar_solicitacoes_senha,
        name='gerenciar_solicitacoes_senha',
    ),
    path('esqueci-senha/', views.solicitar_redefinicao_senha, name='password_reset'),
    path(
        'esqueci-senha/enviado/',
        views.solicitacao_senha_enviada,
        name='password_reset_done',
    ),
    path('logout/', views.logout, name='logout'),
    path('painel/', views.painel, name='painel'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/<str:username>/', views.perfil_publico, name='perfil_publico'),
]
