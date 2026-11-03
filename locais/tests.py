import tempfile

from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.html import conditional_escape
from django.test import override_settings
from django.urls import reverse

from .models import FotoLocal, InformacaoLocal, LocalPesca, MUNICIPIOS_RONDONIA


class PaginaLocaisTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='iniciante',
            password='senha-correta',
        )

    def test_usuario_logado_pode_ver_os_locais_principais(self):
        self.client.force_login(self.usuario)

        response = self.client.get(reverse('locais'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rio Guaporé')
        self.assertContains(response, 'Rio Madeira')
        self.assertContains(response, 'Rio Jamari')
        self.assertContains(response, 'images/local1.jpg')
        self.assertContains(response, 'images/local2.jpg')
        self.assertContains(response, 'images/local3.jpg')
        self.assertNotContains(response, 'Adicionar local de pesca')

    def test_usuario_sem_permissao_nao_pode_cadastrar_local(self):
        self.client.force_login(self.usuario)

        response = self.client.post(reverse('locais'), {
            'nome': 'Rio Machado',
            'municipio': 'Ji-Paraná',
            'descricao': 'Ponto de pesca.',
            'maps_url': 'https://maps.google.com/?q=Rio+Machado',
        })

        self.assertEqual(response.status_code, 405)
        self.assertFalse(LocalPesca.objects.exists())

    def test_pescador_pode_ver_formulario_e_cadastrar_local(self):
        pescador, _ = Group.objects.get_or_create(name='Pescador')
        self.usuario.groups.add(pescador)
        self.client.force_login(self.usuario)

        response = self.client.get(reverse('adicionar_local'))
        self.assertContains(response, 'Adicionar local de pesca')
        self.assertContains(response, 'enctype="multipart/form-data"')

        response = self.client.post(reverse('adicionar_local'), {
            'nome': 'Rio Machado',
            'municipio': 'Ji-Paraná',
            'descricao': 'Ponto de pesca na região.',
            'maps_url': 'https://maps.google.com/?q=Rio+Machado',
        })

        self.assertRedirects(response, reverse('locais'))
        local = LocalPesca.objects.get(nome='Rio Machado')
        self.assertEqual(local.cadastrado_por, self.usuario)
        self.assertEqual(local.municipio, 'Ji-Paraná')

    def test_cartao_de_local_principal_abre_pagina_de_detalhes(self):
        response = self.client.get(reverse('locais'))

        self.assertContains(
            response,
            reverse('detalhe_local_principal', args=['rio-guapore']),
        )
        detalhe = self.client.get(
            reverse('detalhe_local_principal', args=['rio-guapore']),
        )

        self.assertEqual(detalhe.status_code, 200)
        self.assertContains(detalhe, 'Rio Guaporé')
        self.assertContains(detalhe, 'location-gallery-title')
        self.assertContains(detalhe, 'images/local1.jpg')

    def test_detalhe_do_local_cadastrado_mostra_informacoes_e_fotos(self):
        local = LocalPesca.objects.create(
            nome='Rio Machado',
            municipio='Ji-Paraná',
            descricao='Acesso pela margem pública.',
            maps_url='https://maps.google.com/?q=Rio+Machado',
            cadastrado_por=self.usuario,
        )

        response = self.client.get(reverse('detalhe_local', args=[local.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Acesso pela margem pública.')
        self.assertContains(response, 'Ji-Paraná')
        self.assertContains(response, 'Abrir localização no Maps')
        self.assertContains(response, 'Ainda não há fotos deste local.')

    def test_pescador_pode_editar_local_com_campos_previamente_preenchidos(self):
        pescador, _ = Group.objects.get_or_create(name='Pescador')
        self.usuario.groups.add(pescador)
        self.client.force_login(self.usuario)
        local = LocalPesca.objects.create(
            nome='Rio Machado',
            municipio='Ji-Paraná',
            descricao='Descrição original.',
            maps_url='https://maps.google.com/?q=Rio+Machado',
            cadastrado_por=self.usuario,
        )

        response = self.client.get(reverse('editar_local', args=[local.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Rio Machado"')
        self.assertContains(response, 'Descrição original.')
        self.assertContains(response, 'Salvar alterações')
        self.assertContains(response, 'Cancelar')

        response = self.client.post(
            reverse('editar_local', args=[local.pk]),
            {
                'nome': 'Rio Machado atualizado',
                'municipio': 'Ji-Paraná',
                'descricao': 'Descrição original.',
                'maps_url': 'https://maps.google.com/?q=Rio+Machado',
            },
        )

        self.assertRedirects(
            response,
            reverse('detalhe_local', args=[local.pk]),
        )
        local.refresh_from_db()
        self.assertEqual(local.nome, 'Rio Machado atualizado')
        self.assertEqual(local.descricao, 'Descrição original.')

    def test_iniciante_nao_pode_editar_local(self):
        self.client.force_login(self.usuario)
        local = LocalPesca.objects.create(
            nome='Rio Machado',
            municipio='Ji-Paraná',
            descricao='Descrição original.',
            maps_url='https://maps.google.com/?q=Rio+Machado',
            cadastrado_por=self.usuario,
        )

        response = self.client.get(reverse('editar_local', args=[local.pk]))

        self.assertEqual(response.status_code, 403)
        response = self.client.post(reverse('editar_local', args=[local.pk]), {
            'nome': 'Rio Machado alterado',
            'municipio': 'Ji-Paraná',
            'descricao': 'Descrição alterada.',
            'maps_url': 'https://maps.google.com/?q=Rio+Machado',
        })
        self.assertEqual(response.status_code, 403)
        local.refresh_from_db()
        self.assertEqual(local.nome, 'Rio Machado')
        self.assertEqual(local.descricao, 'Descrição original.')

    def test_iniciante_apenas_visualiza_locais_sem_acoes_de_edicao(self):
        self.client.force_login(self.usuario)
        local = LocalPesca.objects.create(
            nome='Rio Machado',
            municipio='Ji-Paraná',
            descricao='Descrição original.',
            maps_url='https://maps.google.com/?q=Rio+Machado',
            cadastrado_por=self.usuario,
        )

        lista = self.client.get(reverse('locais'))
        self.assertEqual(lista.status_code, 200)
        self.assertContains(lista, 'Rio Machado')
        self.assertNotContains(lista, 'Adicionar local de pesca')

        detalhe = self.client.get(reverse('detalhe_local', args=[local.pk]))
        self.assertEqual(detalhe.status_code, 200)
        self.assertContains(detalhe, 'Descrição original.')
        self.assertNotContains(detalhe, 'Editar local')
        self.assertNotContains(detalhe, 'Adicionar informações e fotos')

        resposta = self.client.get(reverse('adicionar_local'))
        self.assertEqual(resposta.status_code, 403)
        resposta = self.client.post(reverse('adicionar_local'), {
            'nome': 'Rio Candeias',
            'municipio': 'Candeias do Jamari',
            'descricao': 'Local para pesca.',
            'maps_url': 'https://maps.google.com/?q=Rio+Candeias',
        })
        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(LocalPesca.objects.filter(nome='Rio Candeias').exists())

        resposta = self.client.post(
            reverse('adicionar_informacoes_local', args=[local.pk]),
            {'descricao': 'Informação não autorizada.'},
        )
        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(InformacaoLocal.objects.filter(local=local).exists())

    def test_seletor_pesquisavel_mostra_todos_os_municipios_de_rondonia(self):
        pescador, _ = Group.objects.get_or_create(name='Pescador')
        self.usuario.groups.add(pescador)
        self.client.force_login(self.usuario)

        response = self.client.get(reverse('adicionar_local'))

        self.assertContains(response, 'list="municipios-rondonia"')
        self.assertContains(response, '<datalist id="municipios-rondonia">')
        for municipio, _ in MUNICIPIOS_RONDONIA:
            self.assertContains(
                response,
                f'<option value="{conditional_escape(municipio)}">',
            )
        self.assertEqual(len(MUNICIPIOS_RONDONIA), 52)

    def test_nao_pode_cadastrar_nome_que_nao_seja_municipio_de_rondonia(self):
        pescador, _ = Group.objects.get_or_create(name='Pescador')
        self.usuario.groups.add(pescador)
        self.client.force_login(self.usuario)

        response = self.client.post(reverse('adicionar_local'), {
            'nome': 'Rio Machado',
            'municipio': 'Urbano Santos',
            'descricao': 'Ponto de pesca na região.',
            'maps_url': 'https://maps.google.com/?q=Rio+Machado',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(LocalPesca.objects.exists())
        self.assertContains(
            response,
            'Selecione um município válido de Rondônia.',
        )

    def test_administrador_pode_cadastrar_local(self):
        administrador = User.objects.create_user(
            username='admin',
            password='senha-correta',
            is_staff=True,
        )
        self.client.force_login(administrador)

        response = self.client.post(reverse('adicionar_local'), {
            'nome': 'Rio Candeias',
            'municipio': 'Candeias do Jamari',
            'descricao': 'Local para pesca.',
            'maps_url': 'https://maps.google.com/?q=Rio+Candeias',
        })

        self.assertRedirects(response, reverse('locais'))
        self.assertTrue(LocalPesca.objects.filter(nome='Rio Candeias').exists())

    def test_pescador_pode_enviar_foto_do_local(self):
        pescador, _ = Group.objects.get_or_create(name='Pescador')
        self.usuario.groups.add(pescador)
        self.client.force_login(self.usuario)
        gif = (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
            b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'D\x01\x00;'
        )

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(reverse('adicionar_local'), {
                    'nome': 'Rio Machado',
                    'municipio': 'Ji-Paraná',
                    'descricao': 'Ponto de pesca na região.',
                    'maps_url': 'https://maps.google.com/?q=Rio+Machado',
                    'foto': SimpleUploadedFile(
                        'rio.gif',
                        gif,
                        content_type='image/gif',
                    ),
                })

                self.assertRedirects(response, reverse('locais'))
                local = LocalPesca.objects.get(nome='Rio Machado')
                self.assertTrue(local.foto.storage.exists(local.foto.name))

    def test_pescador_pode_adicionar_fotos_adicionais_ao_local(self):
        pescador, _ = Group.objects.get_or_create(name='Pescador')
        self.usuario.groups.add(pescador)
        self.client.force_login(self.usuario)
        local = LocalPesca.objects.create(
            nome='Rio Machado',
            municipio='Ji-Paraná',
            descricao='Ponto de pesca na região.',
            maps_url='https://maps.google.com/?q=Rio+Machado',
            cadastrado_por=self.usuario,
        )
        gif = (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
            b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'D\x01\x00;'
        )

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse('adicionar_informacoes_local', args=[local.pk]),
                    {
                        'descricao': 'Acesso melhor pela margem norte.',
                        'fotos': [
                            SimpleUploadedFile(
                                'margem.gif',
                                gif,
                                content_type='image/gif',
                            ),
                            SimpleUploadedFile(
                                'rio.gif',
                                gif,
                                content_type='image/gif',
                            ),
                        ],
                    },
                )

                self.assertRedirects(
                    response,
                    reverse('detalhe_local', args=[local.pk]),
                )
                informacao = InformacaoLocal.objects.get(local=local)
                self.assertEqual(
                    informacao.descricao,
                    'Acesso melhor pela margem norte.',
                )
                self.assertEqual(informacao.fotos.count(), 2)
                self.assertEqual(FotoLocal.objects.filter(local=local).count(), 2)
                detalhe = self.client.get(reverse('detalhe_local', args=[local.pk]))
                self.assertContains(detalhe, 'Acesso melhor pela margem norte.')
                self.assertContains(detalhe, '2 fotos')

    def test_usuario_sem_permissao_nao_pode_adicionar_informacao_ao_local(self):
        self.client.force_login(self.usuario)
        local = LocalPesca.objects.create(
            nome='Rio Machado',
            municipio='Ji-Paraná',
            descricao='Ponto de pesca na região.',
            maps_url='https://maps.google.com/?q=Rio+Machado',
            cadastrado_por=self.usuario,
        )

        response = self.client.get(
            reverse('adicionar_informacoes_local', args=[local.pk]),
        )

        self.assertEqual(response.status_code, 403)

    def test_pescador_acessa_formulario_separado_de_informacoes(self):
        pescador, _ = Group.objects.get_or_create(name='Pescador')
        self.usuario.groups.add(pescador)
        self.client.force_login(self.usuario)
        local = LocalPesca.objects.create(
            nome='Rio Machado',
            municipio='Ji-Paraná',
            descricao='Ponto de pesca na região.',
            maps_url='https://maps.google.com/?q=Rio+Machado',
            cadastrado_por=self.usuario,
        )

        response = self.client.get(
            reverse('adicionar_informacoes_local', args=[local.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Novas informações do local')
        self.assertContains(response, 'Fotos adicionais (opcional)')

    def test_usuario_sem_permissao_nao_pode_abrir_o_cadastro_separado(self):
        self.client.force_login(self.usuario)

        response = self.client.get(reverse('adicionar_local'))

        self.assertEqual(response.status_code, 403)

    def test_visitante_pode_ver_locais_cadastrados(self):
        LocalPesca.objects.create(
            nome='Rio Machado',
            municipio='Ji-Paraná',
            descricao='Local compartilhado.',
            maps_url='https://maps.google.com/?q=Rio+Machado',
            cadastrado_por=self.usuario,
        )

        response = self.client.get(reverse('locais'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rio Machado')
        self.assertContains(response, 'Local compartilhado.')
