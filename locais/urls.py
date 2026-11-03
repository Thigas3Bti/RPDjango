from django.urls import path

from . import views


urlpatterns = [
    path('', views.lista_locais, name='locais'),
    path('adicionar/', views.adicionar_local, name='adicionar_local'),
    path('principais/<slug:slug>/', views.detalhe_local_principal, name='detalhe_local_principal'),
    path('<int:pk>/editar/', views.editar_local, name='editar_local'),
    path('<int:pk>/adicionar-informacoes/', views.adicionar_informacoes_local, name='adicionar_informacoes_local'),
    path('<int:pk>/', views.detalhe_local, name='detalhe_local'),
]
