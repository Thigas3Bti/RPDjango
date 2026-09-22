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