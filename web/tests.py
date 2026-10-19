from io import BytesIO
from tempfile import TemporaryDirectory

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from PIL import Image

from .models import Dica


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

    def test_admin_can_publish_tip_and_see_it_in_list(self):
        user = User.objects.create_user(
            username='administrador',
            password='senha-correta',
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.post(reverse('adicionar_dica'), {
            'titulo': 'Ler a correnteza',
            'categoria': 'avancado',
            'descricao': 'Observe onde a corrente muda de velocidade.',
        })

        self.assertRedirects(response, reverse('dicas'))
        dica = Dica.objects.get(titulo='Ler a correnteza')
        self.assertEqual(dica.autor, user)
        self.assertEqual(dica.categoria, 'avancado')
        tips_response = self.client.get(reverse('dicas'))
        self.assertContains(tips_response, 'Ler a correnteza')
        self.assertContains(tips_response, 'DICA DA COMUNIDADE')

    def test_adding_tip_requires_login(self):
        response = self.client.get(reverse('adicionar_dica'))

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("adicionar_dica")}',
        )

    def test_admin_form_shows_only_the_requested_categories(self):
        user = User.objects.create_user(
            username='administrador',
            password='senha-correta',
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('adicionar_dica'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['form'].fields['categoria'].choices),
            [
                ('iniciante', 'Iniciante'),
                ('intermediario', 'Intermediário'),
                ('avancado', 'Avançado'),
                ('veterano', 'Veterano'),
            ],
        )

    def test_regular_user_cannot_open_or_submit_tip_form(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        self.client.force_login(user)

        get_response = self.client.get(reverse('adicionar_dica'))
        post_response = self.client.post(reverse('adicionar_dica'), {
            'titulo': 'Dica não autorizada',
            'categoria': 'iscas',
            'descricao': 'Este conteúdo não deve ser salvo.',
        })

        self.assertEqual(get_response.status_code, 403)
        self.assertEqual(post_response.status_code, 403)
        self.assertEqual(Dica.objects.count(), 0)

    def test_invalid_tip_is_not_saved(self):
        user = User.objects.create_user(
            username='administrador',
            password='senha-correta',
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.post(reverse('adicionar_dica'), {
            'titulo': '',
            'categoria': 'tecnicas',
            'descricao': 'Descrição válida.',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Dica.objects.count(), 0)
        self.assertContains(response, 'Este campo é obrigatório.')

    def test_admin_can_upload_a_valid_image(self):
        user = User.objects.create_user(
            username='administrador',
            password='senha-correta',
            is_staff=True,
        )
        self.client.force_login(user)

        image_buffer = BytesIO()
        Image.new('RGB', (1, 1), color='green').save(image_buffer, format='PNG')
        image = SimpleUploadedFile(
            'dica.png',
            image_buffer.getvalue(),
            content_type='image/png',
        )

        with TemporaryDirectory() as media_directory:
            with override_settings(MEDIA_ROOT=media_directory):
                response = self.client.post(reverse('adicionar_dica'), {
                    'titulo': 'Dica com imagem',
                    'categoria': 'iniciante',
                    'descricao': '',
                    'imagem': image,
                })

                self.assertRedirects(response, reverse('dicas'))
                dica = Dica.objects.get(titulo='Dica com imagem')
                self.assertTrue(dica.imagem.name.startswith('dicas/'))
                self.assertTrue(dica.imagem.storage.exists(dica.imagem.name))

    def test_invalid_image_is_not_saved(self):
        user = User.objects.create_user(
            username='administrador',
            password='senha-correta',
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.post(reverse('adicionar_dica'), {
            'titulo': 'Dica sem imagem válida',
            'categoria': 'iniciante',
            'imagem': SimpleUploadedFile(
                'nao-e-imagem.png',
                b'conteudo invalido',
                content_type='image/png',
            ),
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Dica.objects.count(), 0)
        self.assertContains(response, 'Envie uma imagem válida.')

    def test_upload_with_non_image_extension_is_rejected(self):
        user = User.objects.create_user(
            username='administrador',
            password='senha-correta',
            is_staff=True,
        )
        self.client.force_login(user)

        image_buffer = BytesIO()
        Image.new('RGB', (1, 1), color='green').save(image_buffer, format='PNG')
        response = self.client.post(reverse('adicionar_dica'), {
            'titulo': 'Dica com extensão insegura',
            'categoria': 'iniciante',
            'imagem': SimpleUploadedFile(
                'arquivo.php',
                image_buffer.getvalue(),
                content_type='image/png',
            ),
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Dica.objects.count(), 0)
        self.assertContains(response, 'A extensão de arquivo')


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

        self.assertContains(response, 'Menu do usuário')
        self.assertContains(response, 'Ver perfil')
        self.assertContains(response, f'href="{reverse("perfil")}"')
        self.assertContains(response, reverse('logout'))
        self.assertNotContains(response, '>Entrar</a>')

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

    def test_logout_clears_session_and_redirects_home(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        self.client.force_login(user)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)
