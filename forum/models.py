from django.conf import settings
from django.db import models

from usuarios.models import Usuario


# Create your models here.

class Equipamentos(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    descricao = models.TextField(blank=True, null=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Eventos(models.Model):
    nome = models.CharField(max_length=100)
    data_evento = models.DateField()
    descricao = models.TextField(max_length=5000, blank=True, null=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Locais(models.Model):
    ESTADOS_CHOICES = [
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MS', 'Mato Grosso do Sul'),
        ('MT', 'Mato Grosso'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins')
    ]
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=ESTADOS_CHOICES, default='RO')
    coordenadas = models.CharField(max_length=100, blank=True, null=True)
    descricao = models.TextField(max_length=5000, blank=True, null=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    evento = models.ManyToManyField(Eventos, blank=True)

    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locais'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class TipoPeixes(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Tipo'
        verbose_name_plural = 'Tipos'

    def __str__(self):
        return self.nome

class Peixes(models.Model):
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=100)
    peso = models.FloatField(blank=True, null=True)
    tamanho = models.FloatField(blank=True, null=True)
    Tipo = models.ForeignKey(TipoPeixes, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Peixe'
        verbose_name_plural = 'Peixes'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Publicacao(models.Model):
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publicacoes_forum',
    )
    titulo = models.CharField(max_length=120, blank=True)
    texto = models.TextField(max_length=2000, blank=True)
    foto = models.FileField(upload_to='forum/publicacoes/%Y/%m/', blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Publicação'
        verbose_name_plural = 'Publicações'

    def __str__(self):
        return self.titulo or f'Publicação de {self.autor}'


class Comentario(models.Model):
    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name='comentarios',
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios_forum',
    )
    texto = models.CharField(max_length=500)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'

    def __str__(self):
        return f'Comentário de {self.autor} na publicação {self.publicacao_id}'


class Curtida(models.Model):
    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name='curtidas',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='curtidas_forum',
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['publicacao', 'usuario'],
                name='forum_curtida_unica_por_usuario',
            ),
        ]
        verbose_name = 'Curtida'
        verbose_name_plural = 'Curtidas'

    def __str__(self):
        return f'Curtida de {self.usuario} na publicação {self.publicacao_id}'