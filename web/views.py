from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
import logging
import smtplib

from .forms import (
    DicaForm,
    FotoPerfilForm,
    LoginForm,
    MensagemContatoForm,
    RegistrationForm,
)
from forum.models import EventoAgenda
from .models import Dica, MensagemContato
from usuarios.models import PerfilUsuario
logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


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


def surpresa(request):
    return render(request, 'web/surpresa.html')


def contato(request):
    form = MensagemContatoForm(
        request.POST if request.method == 'POST' else None,
    )
    if request.method == 'POST' and form.is_valid():
        mensagem_contato = form.save()
        assunto = f"[RondoPesca] {mensagem_contato.get_assunto_display()}"
        corpo = (
            f"Nome: {mensagem_contato.nome}\n"
            f"E-mail: {mensagem_contato.email}\n\n"
            f"Mensagem:\n{mensagem_contato.mensagem}"
        )
        try:
            EmailMessage(
                subject=assunto,
                body=corpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_EMAIL],
                reply_to=[mensagem_contato.email],
            ).send(fail_silently=False)
        except (OSError, smtplib.SMTPException):
            logger.exception('Falha ao enviar mensagem do formulário de contato.')
            messages.warning(
                request,
                'Sua mensagem foi registrada, mas não foi possível enviar a notificação por e-mail.',
            )
        else:
            messages.success(request, 'Sua mensagem foi enviada com sucesso!')
        return redirect('contato')
        dados = form.cleaned_data
        assunto = f"[RondoPesca] {dados['assunto']}"
        corpo = (
            f"Nome: {dados['nome']}\n"
            f"E-mail: {dados['email']}\n\n"
            f"Mensagem:\n{dados['mensagem']}"
        )
        try:
            EmailMessage(
                subject=assunto,
                body=corpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_EMAIL],
                reply_to=[dados['email']],
            ).send(fail_silently=False)
        except (OSError, smtplib.SMTPException):
            logger.exception('Falha ao enviar mensagem do formulário de contato.')
            messages.error(
                request,
                'Não foi possível enviar sua mensagem agora. Tente novamente mais tarde.',
            )
        else:
            messages.success(request, 'Sua mensagem foi enviada com sucesso!')
            return redirect('contato')

    return render(request, 'web/contato.html', {'form': form})


@login_required(login_url='login')
def mensagens_contato(request):
    if not request.user.is_active or not request.user.is_staff:
        return HttpResponseForbidden()

    mensagens = MensagemContato.objects.all()
    status = request.GET.get('status', '')
    if status == 'lidas':
        mensagens = mensagens.filter(lida=True)
    elif status == 'nao_lidas':
        mensagens = mensagens.filter(lida=False)
    else:
        status = ''

    assunto = request.GET.get('assunto', '')
    assuntos_validos = {valor for valor, _ in MensagemContato.ASSUNTOS}
    if assunto in assuntos_validos:
        mensagens = mensagens.filter(assunto=assunto)
    else:
        assunto = ''

    busca = request.GET.get('q', '').strip()
    if busca:
        mensagens = mensagens.filter(
            Q(nome__icontains=busca)
            | Q(email__icontains=busca)
            | Q(assunto__icontains=busca)
            | Q(mensagem__icontains=busca)
        )

    return render(request, 'web/mensagens_contato.html', {
        'mensagens_contato': mensagens,
        'total_nao_lidas': MensagemContato.objects.filter(lida=False).count(),
        'status_selecionado': status,
        'assunto_selecionado': assunto,
        'assuntos': MensagemContato.ASSUNTOS,
        'status_selecionado': status if status in ('nao_lidas', 'lidas') else '',
        'assunto_selecionado': assunto,
        'busca': busca,
        'total_nao_lidas': MensagemContato.objects.filter(lida=False).count(),
    })


@login_required(login_url='login')
@require_POST
def atualizar_status_mensagem(request, mensagem_id):
    if not request.user.is_active or not request.user.is_staff:
        return HttpResponseForbidden()
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    mensagem = get_object_or_404(MensagemContato, pk=mensagem_id)
    status = request.POST.get('status')
    if status == 'lida':
        mensagem.lida = True
    elif status == 'nao_lida':
        mensagem.lida = False
    else:
        messages.error(request, 'Situação de mensagem inválida.')
        return redirect('mensagens_contato')

    mensagem.lida = status == 'lida'
    mensagem.save(update_fields=['lida'])
    messages.success(request, 'Situação da mensagem atualizada.')
    return redirect('mensagens_contato')


def surpresa(request):
    return render(request, 'web/surpresa.html')


def dicas(request):
    return render(request, 'web/dicas.html', {
        'dicas_publicadas': Dica.objects.select_related('autor').all(),
        'pode_adicionar_dica': eh_pescador(request.user),
    })


@login_required(login_url='login')
def adicionar_dica(request):
    if not request.user.is_staff:
        raise PermissionDenied

    form = DicaForm(
        data=request.POST if request.method == 'POST' else None,
        files=request.FILES if request.method == 'POST' else None,
    )

    if request.method == 'POST' and form.is_valid():
        dica = form.save(commit=False)
        dica.autor = request.user
        dica.save()
        messages.success(request, 'A dica foi cadastrada com sucesso.')
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
    perfil_usuario, _ = PerfilUsuario.objects.get_or_create(usuario=request.user)
    if request.method == 'POST' and request.POST.get('remover_foto') == '1':
        if perfil_usuario.foto:
            perfil_usuario.foto.delete(save=True)
            messages.success(request, 'Sua foto de perfil foi removida.')
        return redirect('perfil')

    form = FotoPerfilForm(
        request.POST or None,
        request.FILES or None,
        instance=perfil_usuario,
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Sua foto de perfil foi atualizada.')
            return redirect('perfil')

    return render(request, 'usuarios/pescador/perfil.html', {
        'perfil_usuario': perfil_usuario,
        'foto_form': form,
    })


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
        form.save()
        messages.success(request, 'Cadastro realizado. Agora você pode entrar na sua conta.')
        return redirect('login')

    return render(request, 'usuarios/acesso/cadastro.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('home')
