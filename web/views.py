from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import DicaForm, LoginForm, RegistrationForm
from .models import Dica


def home(request):
    return render(request, 'web/home.html')


def contato(request):
    return render(request, 'web/contato.html')


def dicas(request):
    return render(request, 'web/dicas.html', {
        'dicas_publicadas': Dica.objects.select_related('autor').all(),
    })


@login_required(login_url='login')
def adicionar_dica(request):
    form = DicaForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        dica = form.save(commit=False)
        dica.autor = request.user
        dica.save()
        messages.success(request, 'Sua dica foi adicionada com sucesso.')
        return redirect('dicas')

    return render(request, 'web/adicionar_dica.html', {'form': form})


def comunidade(request):
    return render(request, 'comunidade.html')


def publicar(request):
    return render(request, 'publicar.html')


def inicio(request):
    return render(request, 'base.html')


@login_required(login_url='login')
def painel(request):
    return render(request, 'base.html')


@login_required(login_url='login')
def perfil(request):
    return render(request, 'usuarios/pescador/perfil.html')


def login(request):
    form = LoginForm(
        request,
        data=request.POST if request.method == 'POST' else None,
    )

    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.get_user())
        return redirect('painel')

    return render(request, 'usuarios/acesso/login.html', {'form': form})


def cadastro(request):
    form = RegistrationForm(
        request.POST if request.method == 'POST' else None,
    )

    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.save())
        return redirect('painel')

    return render(request, 'usuarios/acesso/cadastro.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('home')
