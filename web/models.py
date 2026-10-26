from django.conf import settings
from django.db import models


class Dica(models.Model):
    CATEGORIAS = [
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
        ('veterano', 'Veterano'),
    ]

    NIVEIS = [
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
        ('veterano', 'Veterano'),
    ]

    titulo = models.CharField(max_length=120)
    nivel = models.CharField(max_length=20, choices=NIVEIS, default='iniciante')
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS,
        default='iniciante',
    )
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='dicas/', blank=True)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dicas_publicadas',
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Dica'
        verbose_name_plural = 'Dicas'

    def __str__(self):
        return self.titulo
