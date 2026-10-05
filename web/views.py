from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def home(request):
    return render(request, 'web/home.html')


def contato(request):
    return render(request, 'web/contato.html')


@login_required(login_url='login')
def painel(request):
    return render(request, 'base.html')


def login(request):
    form = AuthenticationForm(
        request,
        data=request.POST if request.method == 'POST' else None,
    )
    form.fields['username'].label = 'Username'
    form.fields['password'].label = 'Senha'

    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.get_user())
        return redirect('painel')

    return render(request, 'usuarios/acesso/login.html', {'form': form})
