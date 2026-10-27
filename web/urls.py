from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('inicio/', views.inicio, name='inicio'),
    path('contato/', views.contato, name='contato'),
    path('mensagens/', views.mensagens_contato, name='mensagens_contato'),
    path(
        'mensagens/<int:mensagem_id>/status/',
        views.atualizar_status_mensagem,
        name='atualizar_status_mensagem',
    ),
    path('surpresa/', views.surpresa, name='surpresa'),
    path('dicas/', views.dicas, name='dicas'),
    path('dicas/adicionar/', views.adicionar_dica, name='adicionar_dica'),
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('logout/', views.logout, name='logout'),
    path('painel/', views.painel, name='painel'),
    path('perfil/', views.perfil, name='perfil'),
]
