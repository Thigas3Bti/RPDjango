from django.urls import path

from . import views


urlpatterns = [
    path('', views.comunidade, name='comunidade'),
    path('publicar/', views.publicar, name='publicar'),
    path('publicacao/<int:publicacao_id>/comentar/', views.comentar, name='comentar'),
    path('publicacao/<int:publicacao_id>/curtir/', views.curtir, name='curtir'),
]
