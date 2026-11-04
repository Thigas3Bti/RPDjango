from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.views.decorators.http import require_GET

from usuarios.permissoes import eh_pescador

from .forms import InformacaoLocalForm, LocalPescaForm
from .models import FotoLocal, InformacaoLocal, LocalPesca


LOCAIS_PRINCIPAIS = [
    {
        'slug': 'rio-guapore',
        'nome': 'Rio Guaporé',
        'municipio': 'Região de Pimenteiras do Oeste',
        'descricao': 'Conhecido pela grande diversidade de peixes e pelas paisagens de rios e lagos da fronteira oeste de Rondônia.',
        'imagem': 'images/local1.jpg',
        'maps_url': 'https://maps.app.goo.gl/UcLHvGFdjpHQRwX78',
    },
    {
        'slug': 'rio-madeira',
        'nome': 'Rio Madeira',
        'municipio': 'Região de Porto Velho',
        'descricao': 'Um dos grandes rios amazônicos que atravessam Rondônia, com diversos trechos procurados por pescadores.',
        'imagem': 'images/local2.jpg',
        'maps_url': 'https://maps.app.goo.gl/o4tKMEFgiUFLEYgM9',
    },
    {
        'slug': 'rio-jamari',
        'nome': 'Rio Jamari',
        'municipio': 'Região de Ariquemes',
        'descricao': 'Rio bastante conhecido no estado, com pontos de pesca em diferentes trechos e ambientes.',
        'imagem': 'images/local3.jpg',
        'maps_url': 'https://maps.app.goo.gl/7GfCiWPHknjcaJTc7',
    },
]


@require_GET
def lista_locais(request):
    permissao_cadastro = eh_pescador(request.user)
    return render(request, 'locais/locais.html', {
        'locais_principais': LOCAIS_PRINCIPAIS,
        'locais_cadastrados': LocalPesca.objects.select_related('cadastrado_por'),
        'pode_adicionar_local': permissao_cadastro,
    })


@login_required(login_url='login')
def adicionar_local(request):
    if not eh_pescador(request.user):
        raise PermissionDenied

    form = LocalPescaForm(
        request.POST or None,
        request.FILES or None,
    )
    if request.method == 'POST' and form.is_valid():
        fotos_adicionais = form.cleaned_data.pop('fotos')
        local = form.save(commit=False)
        local.cadastrado_por = request.user
        local.save()
        for foto in fotos_adicionais:
            FotoLocal.objects.create(local=local, arquivo=foto)
        messages.success(request, 'Local de pesca adicionado com sucesso.')
        return redirect('locais')

    return render(request, 'locais/adicionar_local.html', {'form': form})


@login_required(login_url='login')
def editar_local(request, pk):
    if not eh_pescador(request.user):
        raise PermissionDenied

    local = get_object_or_404(LocalPesca, pk=pk)
    form = LocalPescaForm(
        request.POST or None,
        request.FILES or None,
        instance=local,
    )
    if request.method == 'POST' and form.is_valid():
        fotos_adicionais = form.cleaned_data.pop('fotos')
        form.save()
        for foto in fotos_adicionais:
            FotoLocal.objects.create(local=local, arquivo=foto)
        messages.success(request, 'Local de pesca atualizado com sucesso.')
        return redirect('detalhe_local', pk=local.pk)

    return render(request, 'locais/editar_local.html', {
        'form': form,
        'local': local,
    })


def detalhe_local_principal(request, slug):
    local = next(
        (local for local in LOCAIS_PRINCIPAIS if local['slug'] == slug),
        None,
    )
    if local is None:
        raise Http404('Local de pesca não encontrado.')

    return render(request, 'locais/detalhe_local.html', {
        'local': local,
        'fotos': [{'url': static(local['imagem']), 'alt': local['nome']}],
        'local_principal': True,
    })


@require_GET
def detalhe_local(request, pk):
    local = get_object_or_404(
        LocalPesca.objects.prefetch_related(
            'fotos',
            'informacoes_adicionais__autor',
            'informacoes_adicionais__fotos',
        ),
        pk=pk,
    )
    fotos = []
    if local.foto:
        fotos.append({'url': local.foto.url, 'alt': local.nome})
    if local.imagem_url:
        fotos.append({'url': local.imagem_url, 'alt': local.nome})
    fotos.extend(
        {'url': foto.arquivo.url, 'alt': local.nome}
        for foto in local.fotos.all()
    )
    informacoes = local.informacoes_adicionais.select_related('autor').prefetch_related('fotos')

    return render(request, 'locais/detalhe_local.html', {
        'local': local,
        'fotos': fotos,
        'pode_adicionar_local': eh_pescador(request.user),
        'informacoes': informacoes,
    })


@login_required(login_url='login')
def adicionar_informacoes_local(request, pk):
    if not eh_pescador(request.user):
        raise PermissionDenied

    local = get_object_or_404(LocalPesca, pk=pk)
    form = InformacaoLocalForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        informacao = InformacaoLocal.objects.create(
            local=local,
            autor=request.user,
            descricao=form.cleaned_data['descricao'],
        )
        for foto in form.cleaned_data['fotos']:
            FotoLocal.objects.create(
                local=local,
                informacao=informacao,
                arquivo=foto,
            )
        messages.success(request, 'Informações e fotos adicionadas ao local.')
        return redirect('detalhe_local', pk=local.pk)

    return render(request, 'locais/adicionar_informacoes.html', {
        'local': local,
        'form': form,
    })
