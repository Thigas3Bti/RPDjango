from django.urls import path

from . import views


urlpatterns = [
    path('eventos/', views.eventos, name='eventos'),
    path('eventos/criar/', views.criar_evento, name='criar_evento'),
    path('eventos/<int:evento_id>/editar/', views.editar_evento, name='editar_evento'),
    path('eventos/<int:evento_id>/excluir/', views.excluir_evento, name='excluir_evento'),
    path('eventos/<int:evento_id>/participar/', views.participar_evento, name='participar_evento'),
    path('', views.comunidade, name='comunidade'),
    path('publicar/', views.publicar, name='publicar'),
    path('publicacao/<int:publicacao_id>/comentar/', views.comentar, name='comentar'),
    path('publicacao/<int:publicacao_id>/curtir/', views.curtir, name='curtir'),
]
