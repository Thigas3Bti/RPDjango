from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_alter_dica_categoria'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='Dica'),
            ],
        ),
    ]
