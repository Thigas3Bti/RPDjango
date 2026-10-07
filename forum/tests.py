import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Comentario, Curtida, Publicacao


class ComunidadeTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.autor = user_model.objects.create_user(
            username='pescador',
            password='senha-segura-123',
            first_name='Pescador',
        )
        self.outro_usuario = user_model.objects.create_user(
            username='amigo',
            password='senha-segura-456',
        )

    def test_feed_publico_exibe_publicacoes_salvas(self):
        publicacao = Publicacao.objects.create(
            autor=self.autor,
            titulo='Pescaria no rio',
            texto='Uma boa experiência de pesca.',
        )

        resposta = self.client.get(reverse('comunidade'))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, publicacao.titulo)
        self.assertContains(resposta, publicacao.texto)
        self.assertContains(resposta, self.autor.username)

    def test_usuario_autenticado_cria_publicacao_persistente(self):
        self.client.force_login(self.autor)

        resposta = self.client.post(reverse('publicar'), {
            'titulo': 'Dica de isca',
            'texto': 'Experimente uma isca adequada à espécie.',
        })

        self.assertRedirects(resposta, reverse('comunidade'))
        publicacao = Publicacao.objects.get(titulo='Dica de isca')
        self.assertEqual(publicacao.autor, self.autor)

        self.client.logout()
        resposta_feed = self.client.get(reverse('comunidade'))
        self.assertContains(resposta_feed, 'Dica de isca')

    def test_foto_da_publicacao_e_salva_no_servidor(self):
        self.client.force_login(self.autor)
        conteudo_gif = (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
            b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'D\x01\x00;'
        )

        with tempfile.TemporaryDirectory() as pasta_midias:
            with override_settings(MEDIA_ROOT=pasta_midias):
                resposta = self.client.post(reverse('publicar'), {
                    'titulo': 'Foto da pescaria',
                    'foto': SimpleUploadedFile(
                        'pescaria.gif',
                        conteudo_gif,
                        content_type='image/gif',
                    ),
                })

                self.assertRedirects(resposta, reverse('comunidade'))
                publicacao = Publicacao.objects.get(titulo='Foto da pescaria')
                self.assertTrue(publicacao.foto.storage.exists(publicacao.foto.name))

    def test_visitante_precisa_entrar_para_publicar(self):
        resposta = self.client.get(reverse('publicar'))

        self.assertRedirects(
            resposta,
            f"{reverse('login')}?next={reverse('publicar')}",
        )

    def test_comentar_e_curtir_publicacao(self):
        publicacao = Publicacao.objects.create(
            autor=self.autor,
            texto='Post da comunidade.',
        )
        self.client.force_login(self.outro_usuario)

        resposta_comentario = self.client.post(
            reverse('comentar', args=[publicacao.pk]),
            {'texto': 'Ótima dica!'},
        )
        self.assertRedirects(
            resposta_comentario,
            f"{reverse('comunidade')}#publicacao-{publicacao.pk}",
        )
        self.assertTrue(
            Comentario.objects.filter(
                publicacao=publicacao,
                autor=self.outro_usuario,
                texto='Ótima dica!',
            ).exists()
        )

        url_curtida = reverse('curtir', args=[publicacao.pk])
        self.client.post(url_curtida)
        self.assertTrue(
            Curtida.objects.filter(
                publicacao=publicacao,
                usuario=self.outro_usuario,
            ).exists()
        )
        self.client.post(url_curtida)
        self.assertFalse(
            Curtida.objects.filter(
                publicacao=publicacao,
                usuario=self.outro_usuario,
            ).exists()
        )
