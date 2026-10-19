from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth import (
    get_user_model,
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import DicaForm, LoginForm, RegistrationForm
from forum.models import EventoAgenda
from .models import Dica


def _eventos_proximos(user):
    hoje = timezone.localdate()
    eventos = EventoAgenda.objects.filter(
        data_evento__gte=hoje,
    )
    if user.is_authenticated:
        eventos = eventos.filter(
            Q(tipo__in=EventoAgenda.TIPOS_PUBLICOS)
            | Q(tipo=EventoAgenda.TIPO_PESSOAL, organizador=user)
        )
    else:
        eventos = eventos.filter(tipo__in=EventoAgenda.TIPOS_PUBLICOS)
    return eventos.select_related('organizador')[:3]


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
    return render(request, 'base.html', {
        'eventos_proximos': _eventos_proximos(request.user),
    })


@login_required(login_url='login')
def painel(request):
    return render(request, 'base.html', {
        'eventos_proximos': _eventos_proximos(request.user),
    })


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
        try:
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                confirmation_url = request.build_absolute_uri(
                    reverse(
                        'confirmar_email',
                        kwargs={'uidb64': uid, 'token': token},
                    )
                )
                send_mail(
                    'Confirme seu e-mail - RondoPesca',
                    (
                        f'Olá, {user.first_name or user.username}!\n\n'
                        'Para confirmar seu endereço de e-mail e ativar sua conta, '
                        f'accesse o link:\n{confirmation_url}\n\n'
                        'Se você não solicitou este cadastro, ignore esta mensagem.'
                    ),
                    None,
                    [user.email],
                    fail_silently=False,
                )
        except (OSError, SMTPException):
            form.add_error(
                None,
                'Não foi possível enviar o e-mail de confirmação. '
                'Verifique a configuração de e-mail e tente novamente.',
            )
        else:
            messages.success(
                request,
                'Cadastro realizado. Confira seu e-mail para confirmar a conta.',
            )
            return redirect('login')

    return render(request, 'usuarios/acesso/cadastro.html', {'form': form})


def confirmar_email(request, uidb64, token):
    user_model = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = user_model._default_manager.get(pk=uid)
    except (
        TypeError,
        ValueError,
        OverflowError,
        UnicodeDecodeError,
        user_model.DoesNotExist,
    ):
        user = None

    if (
        user is not None
        and not user.is_active
        and default_token_generator.check_token(user, token)
    ):
        user.is_active = True
        user.save(update_fields=['is_active'])
        messages.success(request, 'E-mail confirmado. Agora você pode entrar na sua conta.')
    else:
        messages.error(
            request,
            'O link de confirmação é inválido ou expirou. Faça o cadastro novamente.',
        )
    return redirect('login')


def logout(request):
    auth_logout(request)
    return redirect('home')
