from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .permissoes import eh_pescador


class GerenciarPescadoresTests(TestCase):
    def setUp(self):
        self.administrador = get_user_model().objects.create_user(
            username='admin',
            password='senha-segura-123',
            is_staff=True,
        )
        self.usuario = get_user_model().objects.create_user(
            username='usuario',
            password='senha-segura-123',
        )

    def test_eh_pescador_reconhece_grupo_admin_e_usuario_sem_permissao(self):
        self.assertFalse(eh_pescador(self.usuario))
        self.assertTrue(eh_pescador(self.administrador))

        grupo, _ = Group.objects.get_or_create(name='Pescador')
        self.usuario.groups.add(grupo)
        self.assertTrue(eh_pescador(self.usuario))

        self.usuario.is_active = False
        self.usuario.save(update_fields=['is_active'])
        self.assertFalse(eh_pescador(self.usuario))

    def test_only_staff_can_manage_official_fishermen(self):
        response = self.client.get(reverse('gerenciar_pescadores'))
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("gerenciar_pescadores")}',
        )

        self.client.force_login(self.usuario)
        response = self.client.get(reverse('gerenciar_pescadores'))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            reverse('atualizar_status_pescador', args=[self.usuario.pk]),
            {'acao': 'promover'},
        )
        self.assertEqual(response.status_code, 403)
        grupo = Group.objects.get(name='Pescador')
        self.assertFalse(grupo.user_set.filter(pk=self.usuario.pk).exists())

    def test_staff_can_promote_and_remove_fisherman_status(self):
        self.client.force_login(self.administrador)
        response = self.client.get(reverse('gerenciar_pescadores'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin-page-hero')
        self.assertContains(response, self.usuario.username)
        self.assertContains(response, 'Promover')

        response = self.client.post(
            reverse('atualizar_status_pescador', args=[self.usuario.pk]),
            {'acao': 'promover'},
        )
        self.assertRedirects(response, reverse('gerenciar_pescadores'))
        grupo = Group.objects.get(name='Pescador')
        self.assertTrue(grupo.user_set.filter(pk=self.usuario.pk).exists())

        response = self.client.post(
            reverse('atualizar_status_pescador', args=[self.usuario.pk]),
            {'acao': 'remover'},
        )
        self.assertRedirects(response, reverse('gerenciar_pescadores'))
        self.assertFalse(grupo.user_set.filter(pk=self.usuario.pk).exists())

    def test_promocao_rejects_get(self):
        self.client.force_login(self.administrador)
        response = self.client.get(
            reverse('atualizar_status_pescador', args=[self.usuario.pk]),
        )

        self.assertEqual(response.status_code, 405)

    def test_invalid_action_does_not_change_fisherman_status(self):
        self.client.force_login(self.administrador)
        response = self.client.post(
            reverse('atualizar_status_pescador', args=[self.usuario.pk]),
            {'acao': 'alterar'},
        )

        self.assertRedirects(response, reverse('gerenciar_pescadores'))
        self.assertFalse(
            Group.objects.get(name='Pescador').user_set.filter(
                pk=self.usuario.pk,
            ).exists()
        )
