from django.shortcuts import render
from .models import Usuario


def lista_usuarios(request):
    usuarios = Usuario.objects.all()

    contexto = {
        'usuarios': usuarios
    }

    return render(request, 'usuarios/lista.html', contexto)