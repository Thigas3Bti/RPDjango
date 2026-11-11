from django.contrib import messages
from django.contrib.auth import (
    update_session_auth_hash,
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import Q
from django.forms import ImageField
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
import logging
import smtplib

from .forms import (
    BioPerfilForm,
    DicaForm,
    EditarPerfilForm,
    EquipamentoForm,
    FotoPerfilForm,
    LoginForm,
    RegistrationForm,
    MensagemContatoForm,
    RegistrationPersonalForm,
    SenhaPerfilForm,
    SolicitarRedefinicaoSenhaForm,
)
from forum.models import Dica, EventoAgenda
from usuarios.permissoes import eh_pescador
from .models import (
    Equipamento,
    FotoAdicionalEquipamento,
    MensagemContato,
    SolicitacaoRedefinicaoSenha,
)
from usuarios.models import PerfilUsuario
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
    assunto_inicial = request.GET.get('assunto', '').strip()
    valid_assuntos = {valor for valor, _ in MensagemContato.ASSUNTOS}
    initial = {'assunto': assunto_inicial} if assunto_inicial in valid_assuntos else {}
    form = MensagemContatoForm(
        request.POST if request.method == 'POST' else None,
        initial=initial,
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
        'busca': busca,
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


def solicitar_redefinicao_senha(request):
    form = SolicitarRedefinicaoSenhaForm(
        request.POST if request.method == 'POST' else None,
    )
    if request.method == 'POST' and form.is_valid():
        dados = form.cleaned_data
        SolicitacaoRedefinicaoSenha.objects.create(
            usuario=dados['usuario'],
            email=dados['email'],
            senha_solicitada=make_password(dados['nova_senha']),
        )
        return redirect('password_reset_done')
    return render(request, 'usuarios/acesso/recuperar_senha.html', {'form': form})


def solicitacao_senha_enviada(request):
    return render(request, 'usuarios/acesso/recuperar_senha_enviado.html')


@login_required(login_url='login')
def gerenciar_solicitacoes_senha(request):
    if not request.user.is_active or not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'POST':
        solicitacao = get_object_or_404(
            SolicitacaoRedefinicaoSenha,
            pk=request.POST.get('solicitacao_id'),
            atendida_em__isnull=True,
        )
        usuario = get_user_model().objects.filter(
            username=solicitacao.usuario,
            email__iexact=solicitacao.email,
            is_active=True,
        ).first()
        if usuario is None:
            messages.error(
                request,
                'Não foi encontrada uma conta ativa que corresponda ao nome de usuário e e-mail informados.',
            )
        elif not solicitacao.senha_solicitada:
            messages.error(
                request,
                'Esta solicitação não contém uma nova senha. Peça à pessoa para enviar uma nova solicitação.',
            )
        elif request.POST.get('confirmar_identidade') != '1':
            messages.error(
                request,
                'Confirme que verificou a identidade da pessoa antes de aprovar a alteração.',
            )
        else:
            with transaction.atomic():
                usuario.password = solicitacao.senha_solicitada
                usuario.save(update_fields=['password'])
                solicitacao.senha_solicitada = ''
                solicitacao.atendida_em = timezone.now()
                solicitacao.atendida_por = request.user
                solicitacao.save(update_fields=[
                    'senha_solicitada',
                    'atendida_em',
                    'atendida_por',
                ])
            messages.success(
                request,
                f'A nova senha solicitada para {usuario.username} foi ativada. Avise a pessoa por um canal seguro.',
            )
            return redirect('gerenciar_solicitacoes_senha')
    elif request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])

    solicitacoes = []
    for solicitacao in SolicitacaoRedefinicaoSenha.objects.all():
        usuario = get_user_model().objects.filter(
            username=solicitacao.usuario,
            email__iexact=solicitacao.email,
            is_active=True,
        ).first()
        solicitacoes.append({
            'solicitacao': solicitacao,
            'usuario_encontrado': usuario is not None,
        })

    return render(request, 'web/solicitacoes_senha.html', {
        'solicitacoes': solicitacoes,
    })


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
        messages.success(request, 'Sua dica foi adicionada com sucesso.')
        return redirect('dicas')

    return render(request, 'web/adicionar_dica.html', {'form': form})


def equipamentos(request):
    return render(request, 'web/equipamentos.html', {
        'equipamentos': Equipamento.objects.filter(ativo=True),
    })


def detalhe_equipamento(request, equipamento_id):
    equipamento = get_object_or_404(
        Equipamento.objects.filter(ativo=True),
        pk=equipamento_id,
    )
    outros_equipamentos = list(
        Equipamento.objects.filter(
            ativo=True,
            categoria=equipamento.categoria,
        ).exclude(pk=equipamento.pk)[:4]
    )
    if len(outros_equipamentos) < 4:
        outros_ids = [equipamento.pk, *(item.pk for item in outros_equipamentos)]
        outros_equipamentos.extend(
            Equipamento.objects.filter(ativo=True)
            .exclude(pk__in=outros_ids)
            .exclude(categoria=equipamento.categoria)[:4 - len(outros_equipamentos)]
        )
    fotos_equipamento = []
    if equipamento.foto:
        fotos_equipamento.append(equipamento.foto)
    fotos_equipamento.extend(
        foto_adicional.foto
        for foto_adicional in equipamento.fotos_adicionais.all()
    )

    return render(request, 'web/detalhe_equipamento.html', {
        'equipamento': equipamento,
        'outros_equipamentos': outros_equipamentos,
        'fotos_equipamento': fotos_equipamento,
    })


@login_required(login_url='login')
def cadastrar_equipamento(request):
    if not request.user.is_staff:
        raise PermissionDenied

    form = EquipamentoForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        fotos = request.FILES.getlist('fotos')
        imagens_validas = bool(fotos)
        if not fotos:
            form.add_error(None, 'Adicione pelo menos uma foto do equipamento.')
        else:
            campo_imagem = ImageField()
            for foto in fotos:
                try:
                    campo_imagem.clean(foto)
                except ValidationError:
                    form.add_error(None, f'A foto "{foto.name}" não é uma imagem válida.')
                    imagens_validas = False

        if imagens_validas and form.is_valid():
            equipamento = form.save(commit=False)
            equipamento.foto = fotos[0]
            equipamento.save()
            for foto in fotos[1:]:
                FotoAdicionalEquipamento.objects.create(
                    equipamento=equipamento,
                    foto=foto,
                )
            messages.success(request, 'Equipamento cadastrado com sucesso.')
            return redirect('equipamentos')

    return render(request, 'web/cadastrar_equipamento.html', {'form': form})


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
        'eh_pescador': eh_pescador(request.user),
    })


def perfil_publico(request, username):
    usuario = get_object_or_404(get_user_model(), username=username, is_active=True)
    perfil_usuario = PerfilUsuario.objects.filter(usuario=usuario).first()
    return render(request, 'usuarios/pescador/perfil_publico.html', {
        'usuario_perfil': usuario,
        'perfil_usuario': perfil_usuario,
        'eh_pescador': eh_pescador(usuario),
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
