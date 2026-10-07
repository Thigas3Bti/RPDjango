from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('inicio/', views.inicio, name='inicio'),
    path('contato/', views.contato, name='contato'),
    path('comunidade/', views.comunidade, name='comunidade'),
    path('comunidade/publicar/', views.publicar, name='publicar'),
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('logout/', views.logout, name='logout'),
    path('painel/', views.painel, name='painel'),
    path('perfil/', views.perfil, name='perfil'),
]
