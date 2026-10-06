from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('contato/', views.contato, name='contato'),
    path('login/', views.login, name='login'),
    path('painel/', views.painel, name='painel'),
]
