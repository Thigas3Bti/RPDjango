from django.contrib import messages
from django.contrib.auth import (
    update_session_auth_hash,
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
import logging
import smtplib

from .forms import (
    BioPerfilForm,
    EditarPerfilForm,
    FotoPerfilForm,
    LoginForm,
    RegistrationForm,
    MensagemContatoForm,
    RegistrationPersonalForm,
    SenhaPerfilForm,
)
from forum.models import EventoAgenda
from .models import MensagemContato
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
    foto_form = FotoPerfilForm(instance=perfil_usuario)
    bio_form = BioPerfilForm(instance=perfil_usuario)
    editar_bio = False

    if request.method == 'POST':
        if 'atualizar_foto' in request.POST or 'foto' in request.FILES:
            foto_form = FotoPerfilForm(
                request.POST,
                request.FILES,
                instance=perfil_usuario,
            )
            if foto_form.is_valid():
                foto_form.save()
                messages.success(request, 'Sua foto de perfil foi atualizada.')
                return redirect('perfil')
        elif 'atualizar_bio' in request.POST:
            bio_form = BioPerfilForm(request.POST, instance=perfil_usuario)
            if bio_form.is_valid():
                bio_form.save()
                messages.success(request, 'Sua bio foi atualizada.')
                return redirect('perfil')
            editar_bio = True
        elif request.POST.get('remover_foto') == '1':
            if perfil_usuario.foto:
                perfil_usuario.foto.delete(save=True)
                messages.success(request, 'Sua foto de perfil foi removida.')
            return redirect('perfil')

    return render(request, 'usuarios/pescador/perfil.html', {
        'perfil_usuario': perfil_usuario,
        'foto_form': foto_form,
        'bio_form': bio_form,
        'editar_bio': editar_bio,
    })


@login_required(login_url='login')
def editar_perfil(request):
    perfil_usuario, _ = PerfilUsuario.objects.get_or_create(usuario=request.user)
    secao = request.GET.get('secao', 'pessoal')
    if secao not in ('pessoal', 'seguranca'):
        secao = 'pessoal'

    perfil_form = EditarPerfilForm(instance=request.user)
    bio_form = BioPerfilForm(instance=perfil_usuario)
    senha_form = SenhaPerfilForm(request.user)

    if request.method == 'POST':
        if 'salvar_perfil' in request.POST:
            perfil_form = EditarPerfilForm(request.POST, instance=request.user)
            bio_form = BioPerfilForm(request.POST, instance=perfil_usuario)
            secao = 'pessoal'
            if perfil_form.is_valid() and bio_form.is_valid():
                perfil_form.save()
                bio_form.save()
                messages.success(request, 'Suas informações foram atualizadas.')
                return redirect('editar_perfil')
        elif 'alterar_senha' in request.POST:
            senha_form = SenhaPerfilForm(request.user, request.POST)
            secao = 'seguranca'
            if senha_form.is_valid():
                user = senha_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Sua senha foi alterada.')
                return redirect(f'{reverse("editar_perfil")}?secao=seguranca')

    return render(request, 'usuarios/pescador/editar_perfil.html', {
        'perfil_form': perfil_form,
        'bio_form': bio_form,
        'senha_form': senha_form,
        'secao': secao,
    })


def login(request):
    credenciais_cadastro = None
    initial = None
    if request.method == 'GET':
        credenciais_cadastro = request.session.pop('credenciais_cadastro', None)
        if credenciais_cadastro:
            initial = {
                'username': credenciais_cadastro['username'],
                'password': credenciais_cadastro['password'],
            }
    else:
        request.session.pop('credenciais_cadastro', None)

    form = LoginForm(
        request,
        data=request.POST if request.method == 'POST' else None,
        initial=initial,
    )
    if credenciais_cadastro:
        form.fields['password'].widget.render_value = True

    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.get_user())
        return redirect('painel')

    response = render(request, 'usuarios/acesso/login.html', {
        'form': form,
    })
    if credenciais_cadastro:
        response['Cache-Control'] = 'no-store'
    return response


def cadastro(request):
    etapa = (
        request.POST.get('etapa')
        if request.method == 'POST'
        else request.GET.get('etapa', '1')
    )
    dados_pessoais = request.session.get('cadastro_dados_pessoais')

    if etapa == '2' and not dados_pessoais:
        messages.error(request, 'Preencha primeiro suas informações pessoais.')
        return redirect('cadastro')

    if request.method == 'POST' and request.POST.get('voltar') == '1':
        return redirect(f'{reverse("cadastro")}?etapa=1')

    if etapa == '2':
        dados_completos = dict(dados_pessoais)
        dados_completos.update(request.POST.dict() if request.method == 'POST' else {})
        form = RegistrationForm(
            dados_completos if request.method == 'POST' else None,
            initial=dados_pessoais,
        )
        if request.method == 'POST' and form.is_valid():
            usuario = form.save()
            request.session.pop('cadastro_dados_pessoais', None)
            request.session['credenciais_cadastro'] = {
                'username': usuario.get_username(),
                'password': form.cleaned_data['password1'],
            }
            request.session.set_expiry(60)
            messages.success(
                request,
                'Cadastro realizado. Agora você pode entrar na sua conta.',
            )
            return redirect('login')
        form_fields = tuple(form[name] for name in ('username', 'password1', 'password2'))
        response = render(request, 'usuarios/acesso/cadastro.html', {
            'form': form,
            'form_fields': form_fields,
            'etapa': 2,
        })
        return response

    if request.method == 'POST':
        form = RegistrationPersonalForm(request.POST)
        if form.is_valid():
            request.session['cadastro_dados_pessoais'] = form.cleaned_data
            request.session.set_expiry(600)
            return redirect(f'{reverse("cadastro")}?etapa=2')
    else:
        form = RegistrationPersonalForm(initial=dados_pessoais)

    return render(request, 'usuarios/acesso/cadastro.html', {
        'form': form,
        'form_fields': tuple(form[name] for name in ('first_name', 'last_name', 'email')),
        'etapa': 1,
    })


def logout(request):
    auth_logout(request)
    return redirect('home')
