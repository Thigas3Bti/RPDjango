from django.db import models


class MensagemContato(models.Model):
    ASSUNTOS = [
        ('duvida', 'Dúvida'),
        ('problema', 'Problema'),
        ('sugestao', 'Sugestão'),
        ('dica_experiencia', 'Dica ou experiência de pesca'),
        ('profissional', 'Solicitar cargo de pescador profissional'),
        ('outro', 'Outro assunto'),
    ]

    nome = models.CharField(max_length=120)
    email = models.EmailField()
    assunto = models.CharField(max_length=40, choices=ASSUNTOS)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Mensagem de contato'
        verbose_name_plural = 'Mensagens de contato'

    def __str__(self):
        return f'{self.assunto}: {self.nome}'
