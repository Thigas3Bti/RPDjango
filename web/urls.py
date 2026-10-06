from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('inicio/', views.inicio, name='inicio'),
    path('contato/', views.contato, name='contato'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('painel/', views.painel, name='painel'),
]
