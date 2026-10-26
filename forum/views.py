from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import BooleanField, Count, Exists, OuterRef, Prefetch, Q, Value
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ComentarioForm, EventoAgendaForm, PublicacaoForm
from .models import Comentario, Curtida, EventoAgenda, Publicacao


def eventos(request):
    eventos_futuros = EventoAgenda.objects.filter(
        data_evento__gte=timezone.localdate(),
    )
    if request.user.is_authenticated:
        eventos_futuros = eventos_futuros.filter(
            Q(tipo__in=EventoAgenda.TIPOS_PUBLICOS)
            | Q(tipo=EventoAgenda.TIPO_PESSOAL, organizador=request.user)
        )
    else:
        eventos_futuros = eventos_futuros.filter(
            tipo__in=EventoAgenda.TIPOS_PUBLICOS,
        )

    return render(request, 'eventos/lista.html', {
        'eventos': eventos_futuros.select_related('organizador').prefetch_related(
            'participantes',
        ),
    })


@login_required(login_url='login')
def criar_evento(request):
    if request.method == 'POST':
        form = EventoAgendaForm(request.POST, usuario=request.user)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            evento.save()
            if evento.tipo in EventoAgenda.TIPOS_PUBLICOS:
                evento.participantes.add(request.user)
            messages.success(request, 'Seu evento foi adicionado à agenda.')
            return redirect('eventos')
    elif request.method == 'GET':
        form = EventoAgendaForm(usuario=request.user)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

    return render(request, 'eventos/formulario.html', {
        'form': form,
        'titulo': 'Criar evento',
        'botao': 'Adicionar à agenda',
    })


@login_required(login_url='login')
def editar_evento(request, evento_id):
    evento = get_object_or_404(EventoAgenda, pk=evento_id, organizador=request.user)
    if request.method == 'POST':
        form = EventoAgendaForm(
            request.POST,
            instance=evento,
            usuario=request.user,
        )
        if form.is_valid():
            evento = form.save()
            if evento.tipo in EventoAgenda.TIPOS_PUBLICOS:
                evento.participantes.add(request.user)
            else:
                evento.participantes.clear()
            messages.success(request, 'Seu evento foi atualizado.')
            return redirect('eventos')
    elif request.method == 'GET':
        form = EventoAgendaForm(instance=evento, usuario=request.user)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

    return render(request, 'eventos/formulario.html', {
        'form': form,
        'evento': evento,
        'titulo': 'Editar evento',
        'botao': 'Salvar alterações',
    })


@login_required(login_url='login')
@require_POST
def excluir_evento(request, evento_id):
    evento = get_object_or_404(EventoAgenda, pk=evento_id, organizador=request.user)
    evento.delete()
    messages.success(request, 'Seu evento foi removido da agenda.')
    return redirect('eventos')


@login_required(login_url='login')
@require_POST
def participar_evento(request, evento_id):
    evento = get_object_or_404(
        EventoAgenda,
        pk=evento_id,
        tipo__in=EventoAgenda.TIPOS_PUBLICOS,
        data_evento__gte=timezone.localdate(),
    )
    if evento.participantes.filter(pk=request.user.pk).exists():
        evento.participantes.remove(request.user)
        messages.success(request, 'Você não está mais participando deste evento.')
    else:
        evento.participantes.add(request.user)
        messages.success(request, 'Sua participação foi confirmada.')
    return redirect('eventos')


def comunidade(request):
    publicacoes = Publicacao.objects.select_related('autor').annotate(
        total_curtidas=Count('curtidas'),
    ).prefetch_related(
        Prefetch(
            'comentarios',
            queryset=Comentario.objects.select_related('autor'),
        ),
    )

    if request.user.is_authenticated:
        publicacoes = publicacoes.annotate(
            curtida_usuario=Exists(
                Curtida.objects.filter(
                    publicacao=OuterRef('pk'),
                    usuario=request.user,
                ),
            ),
        )
    else:
        publicacoes = publicacoes.annotate(
            curtida_usuario=Value(False, output_field=BooleanField()),
        )

    if request.GET.get('ordenar') == 'popular':
        publicacoes = publicacoes.order_by('-total_curtidas', '-criada_em')

    return render(request, 'comunidade.html', {
        'publicacoes': publicacoes,
        'ordenacao': request.GET.get('ordenar', 'recentes'),
        'comentario_form': ComentarioForm(),
    })


@login_required(login_url='login')
def publicar(request):
    if request.method == 'POST':
        form = PublicacaoForm(request.POST, request.FILES)
        if form.is_valid():
            publicacao = form.save(commit=False)
            publicacao.autor = request.user
            publicacao.save()
            messages.success(request, 'Sua publicação foi compartilhada com a comunidade.')
            return redirect(f"{reverse('comunidade')}#publicacao-{publicacao.pk}")
    elif request.method == 'GET':
        form = PublicacaoForm()
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

    return render(request, 'publicar.html', {'form': form})


@login_required(login_url='login')
@require_POST
def comentar(request, publicacao_id):
    publicacao = get_object_or_404(Publicacao, pk=publicacao_id)
    form = ComentarioForm(request.POST)
    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.publicacao = publicacao
        comentario.autor = request.user
        comentario.save()
    else:
        messages.error(request, 'Escreva um comentário de até 500 caracteres.')

    return redirect(f"{reverse('comunidade')}#publicacao-{publicacao.pk}")


@login_required(login_url='login')
@require_POST
def excluir_publicacao(request, publicacao_id):
    publicacao = get_object_or_404(Publicacao, pk=publicacao_id)
    if publicacao.autor_id != request.user.pk and not request.user.is_staff:
        raise PermissionDenied

    if publicacao.foto:
        publicacao.foto.delete(save=False)
    publicacao.delete()
    messages.success(request, 'A publicação foi excluída.')
    return redirect('comunidade')


@login_required(login_url='login')
@require_POST
def excluir_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, pk=comentario_id)
    if comentario.autor_id != request.user.pk and not request.user.is_staff:
        raise PermissionDenied

    publicacao_id = comentario.publicacao_id
    comentario.delete()
    messages.success(request, 'O comentário foi excluído.')
    return redirect(f"{reverse('comunidade')}#publicacao-{publicacao_id}")


@login_required(login_url='login')
@require_POST
def curtir(request, publicacao_id):
    publicacao = get_object_or_404(Publicacao, pk=publicacao_id)
    curtida, criada = Curtida.objects.get_or_create(
        publicacao=publicacao,
        usuario=request.user,
    )
    if not criada:
        curtida.delete()

    return redirect(f"{reverse('comunidade')}#publicacao-{publicacao.pk}")
