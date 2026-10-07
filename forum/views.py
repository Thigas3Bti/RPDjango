from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import BooleanField, Count, Exists, OuterRef, Prefetch, Value
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ComentarioForm, PublicacaoForm
from .models import Comentario, Curtida, Publicacao


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
            return redirect('comunidade')
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
def curtir(request, publicacao_id):
    publicacao = get_object_or_404(Publicacao, pk=publicacao_id)
    curtida, criada = Curtida.objects.get_or_create(
        publicacao=publicacao,
        usuario=request.user,
    )
    if not criada:
        curtida.delete()

    return redirect(f"{reverse('comunidade')}#publicacao-{publicacao.pk}")
