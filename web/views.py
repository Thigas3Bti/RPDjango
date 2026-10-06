from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm


def home(request):
    return render(request, 'web/home.html')


def contato(request):
    return render(request, 'web/contato.html')


def inicio(request):
    return render(request, 'base.html')


@login_required(login_url='login')
def painel(request):
    return render(request, 'base.html')


def login(request):
    form = LoginForm(
        request,
        data=request.POST if request.method == 'POST' else None,
    )

    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.get_user())
        return redirect('painel')

    return render(request, 'usuarios/acesso/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('home')
