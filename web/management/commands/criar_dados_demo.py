import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from forum.models import Dica, Publicacao
from locais.models import LocalPesca
from web.models import Equipamento


class Command(BaseCommand):
    help = 'Cria dados locais de demonstração de forma idempotente.'

    def handle(self, *args, **options):
        Usuario = get_user_model()
        pescadores, _ = Group.objects.get_or_create(name='Pescador')

        admin, criado = Usuario.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@rondopesca.local',
                'first_name': 'Administrador',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if criado:
            senha = os.environ.get('DEMO_PASSWORD', 'rondopesca123')
            admin.set_password(senha)
            admin.save()

        pescador, _ = Usuario.objects.get_or_create(
            username='pescador_demo',
            defaults={
                'email': 'pescador@rondopesca.local',
                'first_name': 'Pescador',
            },
        )
        pescador.groups.add(pescadores)

        dica_padrao = (
            'Como escolher o equipamento',
            'iniciante',
            'Para iniciar, escolha uma vara compatível com o tipo de linha e de isca '
            'que pretende usar. Revise anzóis, linha e molinete antes de sair.',
        )
        Dica.objects.get_or_create(
            titulo=dica_padrao[0],
            defaults={
                'nivel': dica_padrao[1],
                'categoria': dica_padrao[1],
                'descricao': dica_padrao[2],
                'autor': admin,
            },
        )

        Equipamento.objects.get_or_create(
            nome='Vara de pesca para iniciantes',
            defaults={
                'categoria': 'vara',
                'descricao': 'Vara versátil para praticar pesca em rios e lagos.',
                'uso': 'Use com linha compatível e sempre revise o estado da ponteira.',
                'ativo': True,
            },
        )

        LocalPesca.objects.get_or_create(
            nome='Rio Madeira - Porto Velho',
            defaults={
                'municipio': 'Porto Velho',
                'descricao': 'Área de referência para demonstrar informações sobre um local de pesca.',
                'imagem_url': '',
                'cadastrado_por': pescador,
            },
        )

        Publicacao.objects.get_or_create(
            autor=pescador,
            titulo='Primeira experiência de demonstração',
            defaults={
                'local_pescaria': 'Rio Madeira',
                'texto': 'Esta publicação inicial permite demonstrar o fluxo da comunidade.',
                'status_moderacao': Publicacao.STATUS_APROVADA,
            },
        )

        self.stdout.write(self.style.SUCCESS('Dados de demonstração preparados.'))
