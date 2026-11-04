from django.urls import path

from . import views


urlpatterns = [
    path('pescadores/', views.gerenciar_pescadores, name='gerenciar_pescadores'),
    path(
        'pescadores/<int:usuario_id>/atualizar/',
        views.atualizar_status_pescador,
        name='atualizar_status_pescador',
    ),
]