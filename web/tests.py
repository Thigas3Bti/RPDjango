from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


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
