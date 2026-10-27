from django.contrib import messages
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

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
    form = MensagemContatoForm(
        request.POST if request.method == 'POST' else None,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Sua mensagem foi enviada com sucesso.')
        return redirect('contato')

    return render(request, 'web/contato.html', {'form': form})


@login_required(login_url='login')
def mensagens_contato(request):
    if not request.user.is_staff:
        raise PermissionDenied

    status = request.GET.get('status', '')
    assunto = request.GET.get('assunto', '')
    busca = request.GET.get('q', '').strip()
    mensagens = MensagemContato.objects.all()

    if status == 'nao_lidas':
        mensagens = mensagens.filter(lida=False)
    elif status == 'lidas':
        mensagens = mensagens.filter(lida=True)

    assuntos_validos = {valor for valor, _ in MensagemContato.ASSUNTOS}
    if assunto in assuntos_validos:
        mensagens = mensagens.filter(assunto=assunto)
    else:
        assunto = ''

    if busca:
        mensagens = mensagens.filter(
            Q(nome__icontains=busca)
            | Q(email__icontains=busca)
            | Q(assunto__icontains=busca)
            | Q(mensagem__icontains=busca)
        )

    return render(request, 'web/mensagens_contato.html', {
        'mensagens_contato': mensagens,
        'assuntos': MensagemContato.ASSUNTOS,
        'status_selecionado': status if status in ('nao_lidas', 'lidas') else '',
        'assunto_selecionado': assunto,
        'busca': busca,
        'total_nao_lidas': MensagemContato.objects.filter(lida=False).count(),
    })


@login_required(login_url='login')
@require_POST
def atualizar_status_mensagem(request, mensagem_id):
    if not request.user.is_staff:
        raise PermissionDenied

    mensagem = get_object_or_404(MensagemContato, pk=mensagem_id)
    status = request.POST.get('status')
    if status not in ('lida', 'nao_lida'):
        messages.error(request, 'Não foi possível atualizar o status da mensagem.')
        return redirect('mensagens_contato')

    mensagem.lida = status == 'lida'
    mensagem.save(update_fields=['lida'])
    messages.success(
        request,
        'Mensagem marcada como lida.'
        if mensagem.lida else 'Mensagem marcada como não lida.',
    )
    return redirect('mensagens_contato')


def surpresa(request):
    return render(request, 'web/surpresa.html')


def dicas(request):
    return render(request, 'web/dicas.html', {
        'dicas_publicadas': Dica.objects.select_related('autor').all(),
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
