from django.core.management import call_command
from django.contrib.staticfiles.management.commands.runserver import (
    Command as DjangoRunserverCommand,
)


class Command(DjangoRunserverCommand):
    def handle(self, *args, **options):
        call_command(
            'migrate',
            interactive=False,
            verbosity=options.get('verbosity', 1),
        )
        return super().handle(*args, **options)
