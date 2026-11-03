from django.db import migrations


def criar_grupo_pescador(apps, schema_editor):
    grupo = apps.get_model('auth', 'Group')
    grupo.objects.get_or_create(name='Pescador')


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('locais', '0005_informacaolocal_fotolocal_informacao'),
    ]

    operations = [
        migrations.RunPython(
            criar_grupo_pescador,
            migrations.RunPython.noop,
        ),
    ]
