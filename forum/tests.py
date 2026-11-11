import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Comentario, Curtida, Dica, EventoAgenda, Publicacao
from usuarios.models import PerfilUsuario


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
        pescadores, _ = Group.objects.get_or_create(name='Pescador')
        self.autor.groups.add(pescadores)
        self.outro_usuario.groups.add(pescadores)

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
        self.assertContains(
            resposta,
            f'href="{reverse("perfil_publico", args=[self.autor.username])}"',
        )

    def test_perfil_publico_do_autor_exibe_bio_e_tipo_de_conta_sem_email(self):
        PerfilUsuario.objects.create(
            usuario=self.autor,
            bio='Gosto de pescar no rio.',
        )
        self.autor.email = 'privado@example.com'
        self.autor.save(update_fields=['email'])

        resposta = self.client.get(
            reverse('perfil_publico', args=[self.autor.username]),
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Gosto de pescar no rio.')
        self.assertContains(resposta, 'Pescador oficial')
        self.assertNotContains(resposta, 'privado@example.com')

    def test_feed_exibe_foto_de_perfil_do_autor(self):
        conteudo_gif = (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
            b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'D\x01\x00;'
        )
        with tempfile.TemporaryDirectory() as pasta_midias:
            with override_settings(MEDIA_ROOT=pasta_midias):
                perfil = PerfilUsuario.objects.create(usuario=self.autor)
                perfil.foto.save(
                    'avatar.gif',
                    SimpleUploadedFile(
                        'avatar.gif',
                        conteudo_gif,
                        content_type='image/gif',
                    ),
                )
                Publicacao.objects.create(
                    autor=self.autor,
                    texto='Publicação com foto de perfil.',
                )
                resposta = self.client.get(reverse('comunidade'))

        self.assertContains(resposta, 'src="/media/perfis/avatar.gif"')

    def test_forum_exibe_link_para_adicionar_dica_a_pescadores_oficiais(self):
        resposta_publica = self.client.get(reverse('comunidade'))

        self.assertContains(resposta_publica, f'href="{reverse("dicas")}"')
        self.assertNotContains(resposta_publica, f'href="{reverse("adicionar_dica")}"')

        self.client.force_login(self.autor)
        resposta_pescador = self.client.get(reverse('comunidade'))
        self.assertContains(
            resposta_pescador,
            f'href="{reverse("adicionar_dica")}"',
        )

        usuario_comum = get_user_model().objects.create_user(
            username='usuario-comum',
            password='senha-segura-123',
        )
        self.client.force_login(usuario_comum)
        resposta_usuario = self.client.get(reverse('comunidade'))
        self.assertNotContains(
            resposta_usuario,
            f'href="{reverse("adicionar_dica")}"',
        )

        administrador = get_user_model().objects.create_user(
            username='administrador',
            password='senha-segura-789',
            is_staff=True,
        )
        self.client.force_login(administrador)
        resposta_admin = self.client.get(reverse('comunidade'))

        self.assertContains(resposta_admin, f'href="{reverse("dicas")}"')
        self.assertContains(resposta_admin, f'href="{reverse("adicionar_dica")}"')

    def test_pagina_de_dicas_exibe_botao_de_adicao_para_pescador_oficial(self):
        rota_adicionar = reverse('adicionar_dica')
        resposta_visitante = self.client.get(reverse('dicas'))
        self.assertNotContains(resposta_visitante, f'href="{rota_adicionar}"')

        usuario_comum = get_user_model().objects.create_user(
            username='usuario-comum-dicas',
            password='senha-segura-123',
        )
        self.client.force_login(usuario_comum)
        resposta_usuario = self.client.get(reverse('dicas'))
        self.assertNotContains(resposta_usuario, f'href="{rota_adicionar}"')

        self.client.force_login(self.autor)
        resposta_pescador = self.client.get(reverse('dicas'))
        self.assertEqual(
            resposta_pescador.content.decode().count(f'href="{rota_adicionar}"'),
            1,
        )

        administrador = get_user_model().objects.create_user(
            username='administrador-dicas',
            password='senha-segura-789',
            is_staff=True,
        )
        self.client.force_login(administrador)
        resposta_admin = self.client.get(reverse('dicas'))

        self.assertEqual(
            resposta_admin.content.decode().count(f'href="{rota_adicionar}"'),
            1,
        )
        self.assertContains(resposta_admin, 'Exibindo todos os níveis.')

    def test_pagina_adicionar_dica_usa_layout_da_pagina_de_dicas(self):
        self.client.force_login(get_user_model().objects.create_user(
            username='autor-dica-layout',
            password='senha-segura-123',
            is_staff=True,
        ))

        resposta = self.client.get(reverse('adicionar_dica'))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'css/forum/dicas.css')
        self.assertContains(resposta, 'class="card dashboard-card learning-form-card')
        self.assertContains(resposta, 'Compartilhe sua dica de pesca')

    def test_dica_da_comunidade_mantem_altura_natural_ao_lado_do_nivel_aberto(self):
        Dica.objects.create(
            autor=self.autor,
            titulo='Dica curta',
            nivel='iniciante',
            categoria='iniciante',
            descricao='Texto curto.',
        )

        resposta = self.client.get(reverse('dicas'))

        self.assertContains(
            resposta,
            '<article class="card dashboard-card learning-community-card shadow-sm p-4">',
        )

    def test_menu_lateral_mantem_dicas_ativa_nas_paginas_do_forum(self):
        self.client.force_login(self.autor)

        for rota in ('dicas', 'adicionar_dica'):
            with self.subTest(rota=rota):
                resposta = self.client.get(reverse(rota))

                self.assertEqual(resposta.status_code, 200)
                self.assertContains(
                    resposta,
                    f'<a href="{reverse("dicas")}" class="nav-link active">Dicas</a>',
                )

    def test_usuario_autenticado_cria_publicacao_persistente(self):
        self.client.force_login(self.autor)

        resposta = self.client.post(reverse('publicar'), {
            'titulo': 'Dica de isca',
            'local_pescaria': 'Rio Madeira',
            'texto': 'Experimente uma isca adequada à espécie.',
        })

        publicacao = Publicacao.objects.get(titulo='Dica de isca')
        self.assertRedirects(
            resposta,
            f"{reverse('comunidade')}#publicacao-{publicacao.pk}",
        )
        self.assertEqual(publicacao.autor, self.autor)
        self.assertEqual(publicacao.local_pescaria, 'Rio Madeira')

        self.client.logout()
        resposta_feed = self.client.get(reverse('comunidade'))
        self.assertContains(resposta_feed, 'Dica de isca')
        self.assertContains(resposta_feed, 'Experimente uma isca adequada à espécie.')
        self.assertContains(resposta_feed, 'Rio Madeira')

    def test_formulario_publicacao_exibe_cabecalho_com_layout_de_fotos(self):
        self.client.force_login(self.autor)

        resposta = self.client.get(reverse('publicar'))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'community-publish-hero')
        self.assertContains(resposta, 'community-publish-hero-art')
        self.assertContains(resposta, 'bi-camera-fill')
        self.assertContains(resposta, 'Conte sua história de pesca')
        self.assertContains(resposta, 'Começar a publicar')

    def test_autor_pode_editar_publicacao_e_ve_acoes_com_icones(self):
        publicacao = Publicacao.objects.create(
            autor=self.autor,
            titulo='Título original',
            texto='Texto original.',
        )
        self.client.force_login(self.autor)

        resposta_feed = self.client.get(reverse('comunidade'))
        self.assertContains(
            resposta_feed,
            f'href="{reverse("editar_publicacao", args=[publicacao.pk])}"',
        )
        self.assertContains(resposta_feed, 'bi-pencil')
        self.assertContains(resposta_feed, 'bi-trash')

        resposta_edicao = self.client.get(
            reverse('editar_publicacao', args=[publicacao.pk]),
        )
        self.assertEqual(resposta_edicao.status_code, 200)
        self.assertContains(resposta_edicao, 'Editar publicação')

        resposta_salvar = self.client.post(
            reverse('editar_publicacao', args=[publicacao.pk]),
            {
                'titulo': 'Título atualizado',
                'local_pescaria': 'Rio Machado',
                'texto': 'Texto atualizado.',
            },
        )
        publicacao.refresh_from_db()
        self.assertRedirects(
            resposta_salvar,
            f"{reverse('comunidade')}#publicacao-{publicacao.pk}",
        )
        self.assertEqual(publicacao.titulo, 'Título atualizado')
        self.assertEqual(publicacao.local_pescaria, 'Rio Machado')
        self.assertEqual(publicacao.texto, 'Texto atualizado.')

    def test_usuario_nao_pode_editar_publicacao_de_outra_pessoa(self):
        publicacao = Publicacao.objects.create(
            autor=self.autor,
            texto='Publicação de outra pessoa.',
        )
        self.client.force_login(self.outro_usuario)

        resposta = self.client.get(
            reverse('editar_publicacao', args=[publicacao.pk]),
        )

        self.assertEqual(resposta.status_code, 403)

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

    def test_usuario_comum_pode_publicar_mas_nao_pode_comentar(self):
        usuario = get_user_model().objects.create_user(
            username='visitante',
            password='senha-segura-789',
        )
        publicacao = Publicacao.objects.create(
            autor=self.autor,
            texto='Publicação existente.',
        )
        self.client.force_login(usuario)

        resposta_publicar = self.client.post(reverse('publicar'), {
            'titulo': 'Não autorizado',
            'texto': 'Esta publicação não deve ser criada.',
        })
        resposta_comentar = self.client.post(
            reverse('comentar', args=[publicacao.pk]),
            {'texto': 'Este comentário não deve ser criado.'},
        )

        nova_publicacao = Publicacao.objects.get(titulo='Não autorizado')
        self.assertRedirects(
            resposta_publicar,
            f"{reverse('comunidade')}#publicacao-{nova_publicacao.pk}",
        )
        self.assertEqual(resposta_comentar.status_code, 403)
        self.assertTrue(Publicacao.objects.filter(
            titulo='Não autorizado',
            autor=usuario,
        ).exists())
        self.assertFalse(Comentario.objects.filter(autor=usuario).exists())

    def test_usuario_comum_ve_botao_para_publicar_mas_nao_formulario_de_comentario(self):
        publicacao = Publicacao.objects.create(
            autor=self.autor,
            texto='Publicação existente.',
        )
        usuario_comum = get_user_model().objects.create_user(
            username='usuario-comum',
            password='senha-segura-987',
        )
        self.client.force_login(usuario_comum)

        resposta = self.client.get(reverse('comunidade'))

        self.assertContains(resposta, f'href="{reverse("publicar")}"')
        self.assertContains(resposta, 'Comentários estão disponíveis para pescadores oficiais.')
        self.assertNotContains(
            resposta,
            f'action="{reverse("comentar", args=[publicacao.pk])}"',
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

    def test_autor_pode_excluir_sua_publicacao(self):
        publicacao = Publicacao.objects.create(
            autor=self.autor,
            titulo='Publicação própria',
            texto='Texto para excluir.',
        )
        self.client.force_login(self.autor)

        resposta = self.client.post(
            reverse('excluir_publicacao', args=[publicacao.pk]),
        )

        self.assertRedirects(resposta, reverse('comunidade'))
        self.assertFalse(Publicacao.objects.filter(pk=publicacao.pk).exists())

    def test_usuario_nao_pode_excluir_publicacao_de_outra_pessoa(self):
        publicacao = Publicacao.objects.create(
            autor=self.autor,
            texto='Publicação de outra pessoa.',
        )
        self.client.force_login(self.outro_usuario)

        resposta = self.client.post(
            reverse('excluir_publicacao', args=[publicacao.pk]),
        )

        self.assertEqual(resposta.status_code, 403)
        self.assertTrue(Publicacao.objects.filter(pk=publicacao.pk).exists())

    def test_moderador_pode_excluir_publicacao_de_outra_pessoa(self):
        publicacao = Publicacao.objects.create(
            autor=self.autor,
            texto='Publicação para moderação.',
        )
        moderador = get_user_model().objects.create_user(
            username='moderador',
            password='senha-segura-789',
            is_staff=True,
        )
        self.client.force_login(moderador)

        resposta = self.client.post(
            reverse('excluir_publicacao', args=[publicacao.pk]),
        )

        self.assertRedirects(resposta, reverse('comunidade'))
        self.assertFalse(Publicacao.objects.filter(pk=publicacao.pk).exists())

    def test_autor_e_moderador_podem_excluir_comentarios(self):
        publicacao = Publicacao.objects.create(
            autor=self.autor,
            texto='Publicação com comentários.',
        )
        comentario_autor = Comentario.objects.create(
            publicacao=publicacao,
            autor=self.autor,
            texto='Comentário meu.',
        )
        self.client.force_login(self.autor)

        resposta_autor = self.client.post(
            reverse('excluir_comentario', args=[comentario_autor.pk]),
        )

        self.assertRedirects(
            resposta_autor,
            f"{reverse('comunidade')}#publicacao-{publicacao.pk}",
        )
        self.assertFalse(Comentario.objects.filter(pk=comentario_autor.pk).exists())

        comentario_alheio = Comentario.objects.create(
            publicacao=publicacao,
            autor=self.outro_usuario,
            texto='Comentário de outra pessoa.',
        )
        resposta_negada = self.client.post(
            reverse('excluir_comentario', args=[comentario_alheio.pk]),
        )
        self.assertEqual(resposta_negada.status_code, 403)
        self.assertTrue(Comentario.objects.filter(pk=comentario_alheio.pk).exists())

        moderador = get_user_model().objects.create_user(
            username='moderador_comentario',
            password='senha-segura-987',
            is_staff=True,
        )
        self.client.force_login(moderador)
        resposta_moderador = self.client.post(
            reverse('excluir_comentario', args=[comentario_alheio.pk]),
        )
        self.assertRedirects(
            resposta_moderador,
            f"{reverse('comunidade')}#publicacao-{publicacao.pk}",
        )
        self.assertFalse(Comentario.objects.filter(pk=comentario_alheio.pk).exists())


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

    def test_agenda_mostra_paineis_de_competicoes_sem_incorporar_site_inteiro(self):
        resposta = self.client.get(reverse('eventos'))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'id="circuito-events-grid"')
        self.assertContains(resposta, 'Etapas disponíveis')
        self.assertNotContains(resposta, '<iframe')
        self.assertContains(
            resposta,
            'href="https://circuitorondonia.com.br/competicoes"',
        )
        self.assertContains(resposta, 'Abrir competições e inscrições')
        self.assertContains(resposta, "js/circuito_eventos.js")

    def test_usuario_cria_evento_pessoal_proprio(self):
        self.client.force_login(self.organizador)
        mapa_iframe = (
            '<iframe src="https://www.google.com/maps/embed?pb=exemplo" '
            'width="600" height="450"></iframe>'
        )

        resposta = self.client.post(reverse('criar_evento'), {
            'nome': 'Minha pescaria',
            'tipo': EventoAgenda.TIPO_PESSOAL,
            'data_evento': self.data_futura.isoformat(),
            'hora_evento': '07:30',
            'local': 'Rio Madeira',
            'mapa_url': mapa_iframe,
            'descricao': 'Levar equipamento.',
        })

        evento = EventoAgenda.objects.get(nome='Minha pescaria')
        self.assertRedirects(resposta, reverse('eventos'))
        self.assertEqual(evento.organizador, self.organizador)
        self.assertFalse(evento.participantes.exists())
        self.assertEqual(
            evento.mapa_url,
            'https://www.google.com/maps/embed?pb=exemplo',
        )

        resposta_agenda = self.client.get(reverse('eventos'))
        self.assertContains(resposta_agenda, 'Rio Madeira')
        self.assertContains(resposta_agenda, '<details class="event-location">')
        self.assertContains(
            resposta_agenda,
            'src="https://www.google.com/maps/embed?pb=exemplo"',
        )

    def test_evento_rejeita_url_de_mapa_que_nao_seja_embed_do_google(self):
        self.client.force_login(self.organizador)

        resposta = self.client.post(reverse('criar_evento'), {
            'nome': 'Evento com mapa inválido',
            'tipo': EventoAgenda.TIPO_PESSOAL,
            'data_evento': self.data_futura.isoformat(),
            'mapa_url': 'https://www.google.com.evil.example/maps/embed?pb=nao-seguro',
        })

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Use uma URL de incorporação segura do Google Maps.')
        self.assertFalse(
            EventoAgenda.objects.filter(nome='Evento com mapa inválido').exists()
        )

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
