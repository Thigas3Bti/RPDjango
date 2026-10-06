from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('contato/', views.contato, name='contato'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('painel/', views.painel, name='painel'),
    path('perfil/', views.perfil, name='perfil'),
]
