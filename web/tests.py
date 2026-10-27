from io import BytesIO
from pathlib import Path
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from PIL import Image

from .models import Dica
from usuarios.models import PerfilUsuario


class ContatoViewTests(TestCase):
    def test_contact_page_uses_shared_template_and_renders(self):
        response = self.client.get(reverse('contato'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fale com o RondoPesca')
        self.assertContains(response, 'href="/contato/"')

    def test_home_contact_call_to_action_points_to_contact_page(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("contato")}"')
        self.assertContains(response, 'Falar conosco')


class DashboardFishingTipsTests(TestCase):
    def test_dedicated_tips_page_displays_each_level_and_filter(self):
        response = self.client.get(reverse('dicas'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="dicas"')
        self.assertContains(response, 'Iniciante: segurança e fundamentos')
        self.assertContains(response, 'Intermediário: local, isca e apresentação')
        self.assertContains(response, 'Avançado: equipamento e leitura da pescaria')
        self.assertContains(response, 'Veterano: análise, adaptação e responsabilidade')
        self.assertContains(response, 'id="filtro-nivel-dicas"')
        self.assertContains(response, 'Adicionar nova dica')

    def test_dashboard_menu_links_to_dedicated_tips_page(self):
        response = self.client.get(reverse('inicio'))

        self.assertContains(response, f'href="{reverse("dicas")}"')
        self.assertNotContains(response, 'id="lista-niveis-dicas"')

    def test_authenticated_user_can_publish_tip_and_see_it_in_list(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        self.client.force_login(user)

        response = self.client.post(reverse('adicionar_dica'), {
            'titulo': 'Ler a correnteza',
            'nivel': 'intermediario',
            'descricao': 'Observe onde a corrente muda de velocidade.',
        })

        self.assertRedirects(response, reverse('dicas'))
        dica = Dica.objects.get(titulo='Ler a correnteza')
        self.assertEqual(dica.autor, user)
        tips_response = self.client.get(reverse('dicas'))
        self.assertContains(tips_response, 'Ler a correnteza')
        self.assertContains(tips_response, 'DICA DA COMUNIDADE')

    def test_adding_tip_requires_login(self):
        response = self.client.get(reverse('adicionar_dica'))

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("adicionar_dica")}',
        )

    def test_invalid_tip_is_not_saved(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        self.client.force_login(user)

        response = self.client.post(reverse('adicionar_dica'), {
            'titulo': '',
            'nivel': 'intermediario',
            'descricao': 'Descrição válida.',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Dica.objects.count(), 0)
        self.assertContains(response, 'Este campo é obrigatório.')


class LoginErrorMessageTests(TestCase):
    def test_shows_message_when_user_does_not_exist(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'nao-existe', 'password': 'senha'},
        )

        self.assertContains(response, 'Usuário não encontrado.')

    def test_shows_message_when_password_is_incorrect(self):
        User.objects.create_user(username='pescador', password='senha-correta')

        response = self.client.post(
            reverse('login'),
            {'username': 'pescador', 'password': 'senha-incorreta'},
        )

        self.assertContains(response, 'Senha incorreta.')


class RegistrationTests(TestCase):
    def test_login_page_links_to_registration(self):
        response = self.client.get(reverse('login'))

        self.assertContains(response, 'Não tem uma conta?')
        self.assertContains(response, f'href="{reverse("cadastro")}"')

    def test_registration_page_renders_account_fields(self):
        response = self.client.get(reverse('cadastro'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar conta')
        self.assertContains(response, 'Confirme a senha')
        self.assertContains(response, 'Escolha um nome de usuário para acessar sua conta.')
        self.assertContains(response, 'Use pelo menos 8 caracteres.')
        self.assertContains(response, 'voce@exemplo.com')

    def test_registration_shows_portuguese_required_field_errors(self):
        response = self.client.post(reverse('cadastro'), {})

        self.assertContains(response, 'Este campo é obrigatório.')

    def test_registration_shows_portuguese_password_mismatch_error(self):
        response = self.client.post(
            reverse('cadastro'),
            {
                'username': 'novo-pescador',
                'first_name': 'Novo',
                'last_name': 'Pescador',
                'email': 'novo@example.com',
                'password1': 'SenhaSegura123!',
                'password2': 'SenhaDiferente123!',
            },
        )

        self.assertContains(response, 'As senhas informadas não são iguais.')

    def test_registration_creates_user_and_logs_them_in(self):
        response = self.client.post(
            reverse('cadastro'),
            {
                'username': 'novo-pescador',
                'first_name': 'Novo',
                'last_name': 'Pescador',
                'email': 'novo@example.com',
                'password1': 'SenhaSegura123!',
                'password2': 'SenhaSegura123!',
            },
        )

        self.assertRedirects(response, reverse('painel'))
        self.assertTrue(User.objects.filter(username='novo-pescador').exists())
        self.assertIn('_auth_user_id', self.client.session)


class UserMenuTests(TestCase):
    def test_authenticated_user_sees_profile_and_logout_menu(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'aria-label="Menu de pescador"')
        self.assertContains(response, 'header-profile-toggle')
        self.assertContains(response, '>pescador</span>')
        self.assertContains(response, 'Ver perfil')
        self.assertContains(response, f'href="{reverse("perfil")}"')
        self.assertContains(response, reverse('logout'))
        self.assertNotContains(response, '>Entrar</a>')

    def test_user_menu_displays_profile_photo_when_available(self):
        user = User.objects.create_user(
            username='pescador',
            password='senha-correta',
            first_name='João',
            last_name='Silva',
        )
        self.client.force_login(user)
        image_file = BytesIO()
        Image.new('RGB', (1, 1), color='green').save(image_file, format='PNG')

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                PerfilUsuario.objects.create(
                    usuario=user,
                    foto=SimpleUploadedFile(
                        'foto.png',
                        image_file.getvalue(),
                        content_type='image/png',
                    ),
                )
                response = self.client.get(reverse('home'))

        self.assertContains(response, 'src="/media/perfis/foto.png"')
        self.assertContains(response, '>João Silva</span>')

    def test_profile_requires_login(self):
        response = self.client.get(reverse('perfil'))

        self.assertRedirects(response, f'{reverse("login")}?next={reverse("perfil")}')

    def test_authenticated_user_can_view_profile(self):
        user = User.objects.create_user(
            username='pescador',
            password='senha-correta',
            first_name='João',
            last_name='Silva',
            email='joao@example.com',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('perfil'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Meu perfil')
        self.assertContains(response, 'João Silva')
        self.assertContains(response, 'joao@example.com')
        self.assertContains(response, 'aria-label="Escolha uma foto de perfil"')
        self.assertContains(response, 'profile-avatar-trigger')
        self.assertContains(response, 'data-bs-target="#profilePhotoModal"')
        self.assertContains(response, 'Adicionar foto de perfil')
        self.assertContains(response, 'Adicionar imagem')
        self.assertContains(response, 'profile-avatar-overlay')
        self.assertContains(response, 'bi-pencil-fill')
        self.assertContains(response, 'Sobre você')
        self.assertContains(response, 'Salvar bio')

    def test_authenticated_user_can_save_profile_bio(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        self.client.force_login(user)

        response = self.client.post(reverse('perfil'), {
            'atualizar_bio': '1',
            'bio': 'Sou pescador e gosto de conhecer novos rios.',
        })

        self.assertRedirects(response, reverse('perfil'))
        perfil = PerfilUsuario.objects.get(usuario=user)
        self.assertEqual(perfil.bio, 'Sou pescador e gosto de conhecer novos rios.')
        profile_response = self.client.get(reverse('perfil'))
        self.assertContains(profile_response, 'Sou pescador e gosto de conhecer novos rios.')

    def test_profile_bio_is_limited_to_500_characters(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        self.client.force_login(user)

        response = self.client.post(reverse('perfil'), {
            'atualizar_bio': '1',
            'bio': 'x' * 501,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Certifique-se de que o valor tenha no máximo 500 caracteres',
        )
        self.assertFalse(PerfilUsuario.objects.filter(usuario=user, bio='x' * 501).exists())

    def test_authenticated_user_can_upload_profile_photo(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        self.client.force_login(user)
        image_file = BytesIO()
        Image.new('RGB', (1, 1), color='green').save(image_file, format='PNG')
        image = SimpleUploadedFile(
            'foto.png',
            image_file.getvalue(),
            content_type='image/png',
        )

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(reverse('perfil'), {'foto': image})

        self.assertRedirects(response, reverse('perfil'))
        perfil = PerfilUsuario.objects.get(usuario=user)
        self.assertTrue(perfil.foto.name.startswith('perfis/'))
        profile_response = self.client.get(reverse('perfil'))
        self.assertContains(profile_response, '/media/perfis/foto.png')
        self.assertContains(profile_response, 'Editar foto de perfil')

    def test_authenticated_user_can_remove_profile_photo(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        self.client.force_login(user)
        image_file = BytesIO()
        Image.new('RGB', (1, 1), color='green').save(image_file, format='PNG')
        image = SimpleUploadedFile(
            'foto.png',
            image_file.getvalue(),
            content_type='image/png',
        )

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                self.client.post(reverse('perfil'), {'foto': image})
                profile_response = self.client.get(reverse('perfil'))
                self.assertContains(profile_response, 'Editar foto de perfil')
                self.assertContains(profile_response, 'Remover imagem')
                response = self.client.post(reverse('perfil'), {'remover_foto': '1'})

                self.assertEqual(response.status_code, 302)
                self.assertEqual(response['Location'], reverse('perfil'))
                perfil = PerfilUsuario.objects.get(usuario=user)
                self.assertFalse(perfil.foto)
                self.assertFalse(list(Path(media_root).rglob('foto.png')))

        self.assertContains(self.client.get(reverse('perfil')), 'Sua foto de perfil foi removida.')

    def test_logout_clears_session_and_redirects_home(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        self.client.force_login(user)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)
