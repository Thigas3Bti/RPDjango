from django.contrib import admin

from .models import Comentario, Curtida, Publicacao

admin.site.register(Publicacao)
admin.site.register(Comentario)
admin.site.register(Curtida)
