from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST


@login_required(login_url='login')
def gerenciar_pescadores(request):
    if not request.user.is_active or not request.user.is_staff:
        raise PermissionDenied

    grupo, _ = Group.objects.get_or_create(name='Pescador')
    usuarios = get_user_model().objects.order_by('username').prefetch_related('groups')
    return render(request, 'usuarios/gerenciar_pescadores.html', {
        'usuarios': usuarios,
        'pescadores_ids': set(grupo.user_set.values_list('pk', flat=True)),
    })


@login_required(login_url='login')
@require_POST
def atualizar_status_pescador(request, usuario_id):
    if not request.user.is_active or not request.user.is_staff:
        raise PermissionDenied

    grupo, _ = Group.objects.get_or_create(name='Pescador')
    usuario = get_object_or_404(get_user_model(), pk=usuario_id)
    acao = request.POST.get('acao')
    if acao == 'promover':
        grupo.user_set.add(usuario)
        messages.success(request, f'{usuario.username} agora é pescador oficial.')
    elif acao == 'remover':
        grupo.user_set.remove(usuario)
        messages.success(request, f'{usuario.username} não é mais pescador oficial.')
    else:
        messages.error(request, 'Ação inválida para o status de pescador.')

    return redirect('gerenciar_pescadores')