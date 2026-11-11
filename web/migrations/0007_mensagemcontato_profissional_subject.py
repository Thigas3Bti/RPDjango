from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_mensagemcontato_lida'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mensagemcontato',
            name='assunto',
            field=models.CharField(
                choices=[
                    ('duvida', 'Dúvida'),
                    ('problema', 'Problema'),
                    ('sugestao', 'Sugestão'),
                    ('dica_experiencia', 'Dica ou experiência de pesca'),
                    ('profissional', 'Solicitar cargo de pescador profissional'),
                    ('outro', 'Outro assunto'),
                ],
                max_length=40,
            ),
        ),
    ]
