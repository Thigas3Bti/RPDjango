import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0005_publicacao_status_moderacao'),
        ('web', '0005_remove_dica_state'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Dica',
                    fields=[
                        ('id', models.BigAutoField(
                            auto_created=True,
                            primary_key=True,
                            serialize=False,
                            verbose_name='ID',
                        )),
                        ('titulo', models.CharField(max_length=120)),
                        ('nivel', models.CharField(
                            choices=[
                                ('iniciante', 'Iniciante'),
                                ('intermediario', 'Intermediário'),
                                ('avancado', 'Avançado'),
                                ('veterano', 'Veterano'),
                            ],
                            default='iniciante',
                            max_length=20,
                        )),
                        ('categoria', models.CharField(
                            choices=[
                                ('iniciante', 'Iniciante'),
                                ('intermediario', 'Intermediário'),
                                ('avancado', 'Avançado'),
                                ('veterano', 'Veterano'),
                            ],
                            default='iniciante',
                            max_length=20,
                        )),
                        ('descricao', models.TextField(blank=True)),
                        ('imagem', models.ImageField(blank=True, upload_to='dicas/')),
                        ('criada_em', models.DateTimeField(auto_now_add=True)),
                        ('autor', models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='dicas_publicadas',
                            to=settings.AUTH_USER_MODEL,
                        )),
                    ],
                    options={
                        'db_table': 'web_dica',
                        'ordering': ['-criada_em'],
                        'verbose_name': 'Dica',
                        'verbose_name_plural': 'Dicas',
                    },
                ),
            ],
        ),
    ]
