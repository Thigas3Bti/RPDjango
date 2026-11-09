from django.contrib import admin

from .models import FotoLocal, InformacaoLocal, LocalPesca


@admin.register(LocalPesca)
class LocalPescaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'municipio', 'cadastrado_por', 'criado_em')
    search_fields = ('nome', 'municipio', 'descricao')
    list_filter = ('criado_em',)


admin.site.register(FotoLocal)
admin.site.register(InformacaoLocal)
