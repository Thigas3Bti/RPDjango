from unittest.mock import call, patch

from django.core.management import get_commands
from django.test import SimpleTestCase

from web.management.commands.runserver import Command


class RunserverMigrationTests(SimpleTestCase):
    def test_project_runserver_command_is_registered(self):
        self.assertEqual(get_commands()['runserver'], 'web')

    @patch('web.management.commands.runserver.DjangoRunserverCommand.run')
    @patch('web.management.commands.runserver.call_command')
    def test_runserver_applies_migrations_before_starting(self, migrate, runserver):
        options = {
            'addrport': '127.0.0.1:8000',
            'use_ipv6': False,
            'verbosity': 0,
        }
        Command().handle(**options)

        migrate.assert_has_calls([
            call('migrate', interactive=False, verbosity=0),
            call('criar_dados_demo', verbosity=0),
        ])
        runserver.assert_called_once_with(**options)
