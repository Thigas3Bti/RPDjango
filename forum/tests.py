import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Comentario, Curtida, EventoAgenda, Publicacao


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

        publicacao = Publicacao.objects.get(titulo='Dica de isca')
        self.assertRedirects(
            resposta,
            f"{reverse('comunidade')}#publicacao-{publicacao.pk}",
        )
        self.assertEqual(publicacao.autor, self.autor)

        self.client.logout()
        resposta_feed = self.client.get(reverse('comunidade'))
        self.assertContains(resposta_feed, 'Dica de isca')
        self.assertContains(resposta_feed, 'Experimente uma isca adequada à espécie.')

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

                publicacao = Publicacao.objects.get(titulo='Foto da pescaria')
                self.assertRedirects(
                    resposta,
                    f"{reverse('comunidade')}#publicacao-{publicacao.pk}",
                )
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


class AgendaEventosTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.organizador = user_model.objects.create_user(
            username='organizador',
            password='senha-segura-123',
        )
        self.outro_usuario = user_model.objects.create_user(
            username='participante',
            password='senha-segura-456',
        )
        self.admin = user_model.objects.create_user(
            username='admin_eventos',
            password='senha-segura-789',
            is_staff=True,
        )
        self.data_futura = timezone.localdate() + timedelta(days=3)

    def criar_evento(self, **kwargs):
        defaults = {
            'nome': 'Pescaria comunitária',
            'data_evento': self.data_futura,
            'tipo': EventoAgenda.TIPO_COMUNIDADE,
            'organizador': self.organizador,
        }
        defaults.update(kwargs)
        return EventoAgenda.objects.create(**defaults)

    def test_agenda_mostra_eventos_comunitarios_e_apenas_eventos_pessoais_do_usuario(self):
        evento_comunitario = self.criar_evento()
        evento_pessoal = self.criar_evento(
            nome='Meu planejamento',
            tipo=EventoAgenda.TIPO_PESSOAL,
        )
        evento_pessoal_alheio = self.criar_evento(
            nome='Planejamento privado',
            tipo=EventoAgenda.TIPO_PESSOAL,
            organizador=self.outro_usuario,
        )
        self.client.force_login(self.organizador)

        resposta = self.client.get(reverse('eventos'))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, evento_comunitario.nome)
        self.assertContains(resposta, evento_pessoal.nome)
        self.assertNotContains(resposta, evento_pessoal_alheio.nome)

    def test_usuario_cria_evento_pessoal_proprio(self):
        self.client.force_login(self.organizador)

        resposta = self.client.post(reverse('criar_evento'), {
            'nome': 'Minha pescaria',
            'tipo': EventoAgenda.TIPO_PESSOAL,
            'data_evento': self.data_futura.isoformat(),
            'hora_evento': '07:30',
            'local': 'Rio Madeira',
            'descricao': 'Levar equipamento.',
        })

        evento = EventoAgenda.objects.get(nome='Minha pescaria')
        self.assertRedirects(resposta, reverse('eventos'))
        self.assertEqual(evento.organizador, self.organizador)
        self.assertFalse(evento.participantes.exists())

    def test_criar_evento_comunitario_inscreve_organizador_e_outros_podem_participar(self):
        self.client.force_login(self.organizador)
        self.client.post(reverse('criar_evento'), {
            'nome': 'Encontro no rio',
            'tipo': EventoAgenda.TIPO_COMUNIDADE,
            'data_evento': self.data_futura.isoformat(),
            'hora_evento': '08:00',
        })
        evento = EventoAgenda.objects.get(nome='Encontro no rio')
        self.assertTrue(evento.participantes.filter(pk=self.organizador.pk).exists())

        self.client.force_login(self.outro_usuario)
        resposta = self.client.post(reverse('participar_evento', args=[evento.pk]))

        self.assertRedirects(resposta, reverse('eventos'))
        self.assertTrue(evento.participantes.filter(pk=self.outro_usuario.pk).exists())

    def test_apenas_admin_pode_criar_evento_oficial(self):
        dados = {
            'nome': 'Campeonato estadual',
            'tipo': EventoAgenda.TIPO_OFICIAL,
            'data_evento': self.data_futura.isoformat(),
            'local': 'Porto Velho',
        }
        self.client.force_login(self.outro_usuario)

        resposta_usuario = self.client.post(reverse('criar_evento'), dados)

        self.assertEqual(resposta_usuario.status_code, 200)
        self.assertFalse(EventoAgenda.objects.filter(nome='Campeonato estadual').exists())

        self.client.force_login(self.admin)
        resposta_admin = self.client.post(reverse('criar_evento'), dados)

        evento = EventoAgenda.objects.get(nome='Campeonato estadual')
        self.assertRedirects(resposta_admin, reverse('eventos'))
        self.assertEqual(evento.tipo, EventoAgenda.TIPO_OFICIAL)
        self.assertTrue(evento.participantes.filter(pk=self.admin.pk).exists())

    def test_evento_oficial_aparece_para_todos_e_aceita_participacao(self):
        evento = self.criar_evento(
            nome='Campeonato aberto',
            tipo=EventoAgenda.TIPO_OFICIAL,
            organizador=self.admin,
        )

        resposta_visitante = self.client.get(reverse('eventos'))
        self.assertContains(resposta_visitante, evento.nome)
        self.assertContains(resposta_visitante, 'Oficial')

        self.client.force_login(self.outro_usuario)
        resposta_participacao = self.client.post(
            reverse('participar_evento', args=[evento.pk]),
        )

        self.assertRedirects(resposta_participacao, reverse('eventos'))
        self.assertTrue(evento.participantes.filter(pk=self.outro_usuario.pk).exists())

    def test_usuario_nao_pode_editar_ou_excluir_evento_de_outra_pessoa(self):
        evento = self.criar_evento()
        self.client.force_login(self.outro_usuario)

        resposta_edicao = self.client.get(reverse('editar_evento', args=[evento.pk]))
        resposta_exclusao = self.client.post(reverse('excluir_evento', args=[evento.pk]))

        self.assertEqual(resposta_edicao.status_code, 404)
        self.assertEqual(resposta_exclusao.status_code, 404)
        self.assertTrue(EventoAgenda.objects.filter(pk=evento.pk).exists())

    def test_tornar_evento_pessoal_remove_participantes_da_comunidade(self):
        evento = self.criar_evento()
        evento.participantes.add(self.outro_usuario)
        self.client.force_login(self.organizador)

        resposta = self.client.post(
            reverse('editar_evento', args=[evento.pk]),
            {
                'nome': evento.nome,
                'tipo': EventoAgenda.TIPO_PESSOAL,
                'data_evento': self.data_futura.isoformat(),
            },
        )

        evento.refresh_from_db()
        self.assertRedirects(resposta, reverse('eventos'))
        self.assertFalse(evento.participantes.exists())

    def test_evento_com_data_passada_nao_pode_ser_criado(self):
        self.client.force_login(self.organizador)

        resposta = self.client.post(reverse('criar_evento'), {
            'nome': 'Evento passado',
            'tipo': EventoAgenda.TIPO_PESSOAL,
            'data_evento': (timezone.localdate() - timedelta(days=1)).isoformat(),
        })

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(EventoAgenda.objects.filter(nome='Evento passado').exists())

    def test_painel_lista_eventos_proximos_sem_expor_evento_pessoal_de_outro_usuario(self):
        self.criar_evento()
        self.criar_evento(
            nome='Meu evento pessoal',
            tipo=EventoAgenda.TIPO_PESSOAL,
        )
        self.criar_evento(
            nome='Evento pessoal privado',
            tipo=EventoAgenda.TIPO_PESSOAL,
            organizador=self.outro_usuario,
        )
        self.client.force_login(self.organizador)

        resposta = self.client.get(reverse('painel'))

        self.assertContains(resposta, 'Pescaria comunitária')
        self.assertContains(resposta, 'Meu evento pessoal')
        self.assertNotContains(resposta, 'Evento pessoal privado')
