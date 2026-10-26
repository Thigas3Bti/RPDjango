from django.contrib import admin

from .models import Comentario, Curtida, Publicacao


@admin.action(description='Aprovar publicações selecionadas')
def aprovar_publicacoes(modeladmin, request, queryset):
    queryset.update(status_moderacao=Publicacao.STATUS_APROVADA)


@admin.action(description='Rejeitar publicações selecionadas')
def rejeitar_publicacoes(modeladmin, request, queryset):
    queryset.update(status_moderacao=Publicacao.STATUS_REJEITADA)


@admin.register(Publicacao)
class PublicacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'criada_em', 'status_moderacao')
    list_filter = ('status_moderacao', 'criada_em')
    search_fields = ('titulo', 'texto', 'autor__username')
    actions = (aprovar_publicacoes, rejeitar_publicacoes)


admin.site.register(Comentario)
admin.site.register(Curtida)
