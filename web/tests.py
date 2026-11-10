from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from forum.models import Dica
from .models import MensagemContato
from usuarios.models import PerfilUsuario


class ContactMessagesAdminTests(TestCase):
    def setUp(self):
        self.dados_mensagem = {
            'nome': 'Pessoa Teste',
            'email': 'pessoa@example.com',
            'assunto': 'problema',
            'mensagem': 'Estou com um problema no cadastro.',
        }

    def test_contact_page_uses_shared_template_and_renders(self):
        response = self.client.get(reverse('contato'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fale com o RondoPesca')
        self.assertContains(response, 'href="/contato/"')
        self.assertContains(response, 'Dúvidas frequentes')
        self.assertContains(response, 'Como faço para criar uma conta?')
        self.assertContains(response, 'href="#duvidas-frequentes"')
        self.assertContains(response, 'class="accordion-button collapsed"')
        self.assertContains(response, 'aria-expanded="false"')
        self.assertNotContains(response, 'accordion-collapse collapse show')

    def test_contact_form_saves_message_and_redirects(self):
        response = self.client.post(reverse('contato'), self.dados_mensagem)

        self.assertRedirects(response, reverse('contato'))
        self.assertEqual(MensagemContato.objects.count(), 1)
        mensagem = MensagemContato.objects.get()
        self.assertEqual(mensagem.nome, self.dados_mensagem['nome'])
        self.assertEqual(mensagem.get_assunto_display(), 'Problema')
        self.assertEqual(mensagem.mensagem, self.dados_mensagem['mensagem'])

    def test_contact_form_saves_professional_role_request(self):
        response = self.client.get(reverse('contato'))
        self.assertContains(response, 'Solicitar cargo de pescador profissional')

        dados = {
            **self.dados_mensagem,
            'assunto': 'profissional',
            'mensagem': 'Solicito a alteração do meu cargo para profissional.',
        }
        response = self.client.post(reverse('contato'), dados)

        self.assertRedirects(response, reverse('contato'))
        mensagem = MensagemContato.objects.get()
        self.assertEqual(mensagem.assunto, 'profissional')
        self.assertEqual(
            mensagem.get_assunto_display(),
            'Solicitar cargo de pescador profissional',
        )

    def test_contact_form_rejects_invalid_email(self):
        dados = {**self.dados_mensagem, 'email': 'email-invalido'}

        response = self.client.post(reverse('contato'), dados)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MensagemContato.objects.count(), 0)
        self.assertContains(response, 'Informe um endereço de email válido.')

    def test_messages_page_requires_staff_user(self):
        response = self.client.get(reverse('mensagens_contato'))
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("mensagens_contato")}',
        )

        user = User.objects.create_user(username='pescador', password='senha')
        self.client.force_login(user)
        response = self.client.get(reverse('mensagens_contato'))
        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_view_submitted_messages(self):
        mensagem = MensagemContato.objects.create(**self.dados_mensagem)
        admin = User.objects.create_user(username='admin', is_staff=True)
        self.client.force_login(admin)

        response = self.client.get(reverse('mensagens_contato'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin-page-hero')
        self.assertContains(response, 'Mensagens recebidas')
        self.assertContains(response, mensagem.nome)

class PerfilEdicaoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='perfil-edicao',
            password='senha-segura-123',
        )
        self.client.force_login(self.user)
        self.perfil = PerfilUsuario.objects.create(usuario=self.user)
        self.addCleanup(self._remover_foto)

    def _remover_foto(self):
        self.perfil.refresh_from_db()
        if self.perfil.foto:
            self.perfil.foto.delete(save=False)

    def test_perfil_exibe_bio_e_controles_de_edicao(self):
        self.perfil.bio = 'Gosto de pesca esportiva.'
        self.perfil.save()

        response = self.client.get(reverse('perfil'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gosto de pesca esportiva.')
        self.assertContains(response, 'Editar')
        self.assertContains(response, 'Cancelar')

    def test_perfil_salva_bio(self):
        response = self.client.post(
            reverse('perfil'),
            {'atualizar_bio': '1', 'bio': 'Minha bio atualizada.'},
        )

        self.assertRedirects(response, reverse('perfil'))
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.bio, 'Minha bio atualizada.')

    def test_bio_invalida_mantem_formulario_em_edicao_sem_salvar(self):
        self.perfil.bio = 'Bio atual.'
        self.perfil.save()

        response = self.client.post(
            reverse('perfil'),
            {'atualizar_bio': '1', 'bio': 'a' * 501},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['editar_bio'])
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.bio, 'Bio atual.')

    def test_perfil_salva_foto_enviada(self):
        image_buffer = BytesIO()
        Image.new('RGB', (1, 1), color='green').save(image_buffer, format='PNG')
        image = SimpleUploadedFile(
            'perfil.png',
            image_buffer.getvalue(),
            content_type='image/png',
        )

        response = self.client.post(
            reverse('perfil'),
            {'atualizar_foto': '1', 'foto': image},
        )

        self.assertRedirects(response, reverse('perfil'))
        self.perfil.refresh_from_db()
        self.assertTrue(self.perfil.foto)

    def test_staff_user_can_filter_messages_by_status_subject_and_search(self):
        MensagemContato.objects.create(**self.dados_mensagem)
        lida = MensagemContato.objects.create(
            **{
                **self.dados_mensagem,
                'nome': 'Outra pessoa',
                'assunto': 'duvida',
                'mensagem': 'Mensagem de dúvida para filtrar.',
            },
            lida=True,
        )
        self.client.force_login(User.objects.create_user(
            username='admin',
            password='senha',
            is_staff=True,
        ))

        response = self.client.get(reverse('mensagens_contato'), {
            'status': 'lidas',
            'assunto': 'duvida',
            'q': 'Outra pessoa',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.message.mensagem)
        self.assertContains(response, 'Solicitar cargo de pescador profissional')
        self.assertEqual(response.context['total_nao_lidas'], 1)

    def test_staff_user_can_mark_message_read_and_unread(self):
        mensagem = MensagemContato.objects.create(**self.dados_mensagem)
        self.client.force_login(User.objects.create_user(
            username='admin',
            password='senha',
            is_staff=True,
        ))
        url = reverse('atualizar_status_mensagem', args=[mensagem.id])

        response = self.client.post(url, {'status': 'lida'})

        self.assertRedirects(response, reverse('mensagens_contato'))
        self.message.refresh_from_db()
        self.assertTrue(self.message.lida)

    def test_message_status_update_rejects_get(self):
        self.client.force_login(User.objects.create_user(
            username='admin',
            password='senha',
            is_staff=True,
        ))

        response = self.client.post(url, {'status': 'nao_lida'})

        self.assertEqual(response.status_code, 405)

    def test_non_staff_cannot_change_message_status(self):
        mensagem = MensagemContato.objects.create(**self.dados_mensagem)
        self.client.force_login(User.objects.create_user(username='pescador'))

class ContatoViewTests(TestCase):
    def test_surprise_page_renders(self):
        response = self.client.get(reverse('surpresa'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Uma surpresa!')
        self.assertContains(response, 'surpresa-1.png')
        self.assertContains(response, 'surpresa-2.png')

    def test_contact_page_uses_shared_template_and_renders(self):
        response = self.client.get(reverse('contato'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fale com o RondoPesca')
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, f'href="{reverse("home")}"')
        self.assertContains(response, 'Voltar')
        self.assertNotContains(response, 'href="/contato/"')

    def test_contact_form_sends_message_to_site_email(self):
        response = self.client.post(reverse('contato'), {
            'nome': 'Maria Pescadora',
            'email': 'maria@example.com',
            'assunto': 'duvida',
            'mensagem': 'Como escolho uma isca?',
        })

        self.assertRedirects(response, reverse('contato'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['rondopescacontato@gmail.com'])
        self.assertIn('Maria Pescadora', mail.outbox[0].body)
        self.assertIn('Como escolho uma isca?', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].reply_to, ['maria@example.com'])
        mensagem = MensagemContato.objects.get()
        self.assertEqual(mensagem.nome, 'Maria Pescadora')
        self.assertEqual(mensagem.assunto, 'duvida')

    def test_contact_form_includes_professional_request_and_records_it(self):
        response = self.client.get(reverse('contato'))
        self.assertContains(response, 'Solicitar cargo de pescador profissional')

        response = self.client.post(reverse('contato'), {
            'nome': 'João Pescador',
            'email': 'joao@example.com',
            'assunto': 'profissional',
            'mensagem': 'Solicito o cargo profissional.',
        })

        self.assertRedirects(response, reverse('contato'))
        mensagem = MensagemContato.objects.get()
        self.assertEqual(mensagem.assunto, 'profissional')
        self.assertIn('profissional', mail.outbox[0].subject.lower())

    def test_contact_form_shows_errors_for_invalid_data(self):
        response = self.client.post(reverse('contato'), {
            'nome': '',
            'email': 'email-invalido',
            'assunto': 'sem-opcao',
            'mensagem': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(response, 'Este campo é obrigatório.')

    def test_home_ctas_point_visitors_to_registration(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("cadastro")}"')
        self.assertContains(response, 'aria-label="Explorar Agora"')
        self.assertContains(response, 'Cadastre-se e explore mais.')
        self.assertContains(response, 'Cadastre-se grátis')
        self.assertContains(response, f'href="{reverse("contato")}"')
        self.assertContains(response, 'Falar conosco')


class SurpresaViewTests(TestCase):
    def test_footer_secret_button_opens_surprise_page(self):
        for page in ('home', 'inicio'):
            with self.subTest(page=page):
                response = self.client.get(reverse(page))

                self.assertContains(response, f'href="{reverse("surpresa")}"')
                self.assertContains(response, 'aria-label="Abrir surpresa"')

    def test_surprise_page_displays_the_attached_image(self):
        response = self.client.get(reverse('surpresa'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Uma surpresa!')
        self.assertContains(response, 'images/surpresa.png')


class SurpresaViewTests(TestCase):
    def test_secret_command_is_loaded_without_a_visible_button(self):
        for page in ('home', 'inicio'):
            with self.subTest(page=page):
                response = self.client.get(reverse(page))

                self.assertContains(response, 'js/base.js?v=20261026-secret-command')
                self.assertContains(response, f'data-surprise-url="{reverse("surpresa")}"')
                self.assertNotContains(response, 'secret-surprise-button')

    def test_surprise_page_displays_the_attached_image(self):
        response = self.client.get(reverse('surpresa'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Uma surpresa!')
        self.assertContains(response, 'images/surpresa-1.png')
        self.assertContains(response, 'images/surpresa-2.png')


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
        self.assertContains(response, 'class="row g-3" id="lista-niveis-dicas"')
        for nivel in ('iniciante', 'intermediario', 'avancado', 'veterano'):
            with self.subTest(nivel=nivel):
                self.assertContains(
                    response,
                    f'class="col-12 col-xl-6 nivel-dica" data-nivel="{nivel}"',
                )
        self.assertNotContains(response, 'Adicionar nova dica')
        self.assertContains(response, 'Somente pescadores oficiais podem adicionar dicas.')

    def test_dashboard_menu_links_to_dedicated_tips_page(self):
        response = self.client.get(reverse('inicio'))

        self.assertContains(
            response,
            'images/banner_tela_inicio.jpg',
        )
        self.assertContains(response, 'images/galeria/local-1.jpg')
        self.assertContains(response, 'images/galeria/local-2.jpg')
        self.assertContains(response, 'images/galeria/local-3.jpg')
        self.assertContains(response, f'href="{reverse("dicas")}"')
        self.assertNotContains(response, 'id="lista-niveis-dicas"')

    def test_authenticated_user_can_publish_tip_and_see_it_in_list(self):
        user = User.objects.create_user(
            username='administrador',
            password='senha-correta',
            is_staff=True,
        )
    def test_admin_can_publish_tip_and_see_it_in_list(self):
        user = User.objects.create_user(
            username='administrador',
            password='senha-correta',
            is_staff=True,
        )
    def test_official_fisherman_can_publish_tip_and_see_it_in_list(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        group, _ = Group.objects.get_or_create(name='Pescador')
        user.groups.add(group)
        self.client.force_login(user)

        response = self.client.post(reverse('adicionar_dica'), {
            'titulo': 'Ler a correnteza',
            'nivel': 'intermediario',
            'descricao': 'Observe onde a corrente muda de velocidade.',
        })

        self.assertRedirects(response, reverse('dicas'))
        dica = Dica.objects.get(titulo='Ler a correnteza')
        self.assertEqual(dica.autor, user)
        self.assertEqual(dica.categoria, 'avancado')
        tips_response = self.client.get(reverse('dicas'))
        self.assertContains(tips_response, 'Ler a correnteza')
        self.assertContains(tips_response, 'DICA DA COMUNIDADE')
        self.assertContains(tips_response, 'Adicionar nova dica')

    def test_adding_tip_requires_login(self):
        response = self.client.get(reverse('adicionar_dica'))

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("adicionar_dica")}',
        )

    def test_regular_user_cannot_publish_tip(self):
        user = User.objects.create_user(username='usuario', password='senha-correta')
        self.client.force_login(user)

        response = self.client.post(reverse('adicionar_dica'), {
            'titulo': 'Dica não autorizada',
            'nivel': 'intermediario',
            'descricao': 'Descrição válida.',
        })
        tips_response = self.client.get(reverse('dicas'))

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Dica.objects.exists())

    def test_invalid_tip_is_not_saved(self):
        user = User.objects.create_user(username='pescador', password='senha-correta')
        group, _ = Group.objects.get_or_create(name='Pescador')
        user.groups.add(group)
        self.client.force_login(user)

        response = self.client.post(reverse('adicionar_dica'), {
            'titulo': '',
            'nivel': 'intermediario',
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
