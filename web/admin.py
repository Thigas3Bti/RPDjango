from django.contrib import admin

from .models import Equipamento


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'ativo', 'criado_em')
    list_filter = ('categoria', 'ativo')
    search_fields = ('nome', 'descricao', 'uso')
