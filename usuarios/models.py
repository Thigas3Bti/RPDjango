from django.conf import settings
from django.db import models

# Create your models here.

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_usuario',
    )
    foto = models.ImageField(upload_to='perfis/', blank=True, null=True)
    bio = models.TextField('bio', blank=True, default='', max_length=500)

    def __str__(self):
        return f'Perfil de {self.usuario}'


class Usuario(models.Model):
    TIPO_CHOICES = [
        ('pescador', 'Pescador'),
        ('outro', 'Outro'),
    ]
    NIVEL_CHOICES = [
        ('iniciante', 'Iniciante'),
        ('avançado', 'Avançado'),
        ('outro', 'Outro'),
    ]
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_nascimento = models.DateField()
    tipo_usuario = models.CharField(max_length=50, choices=TIPO_CHOICES)
    nivel = models.CharField(max_length=50, choices=NIVEL_CHOICES)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nome']

    def __str__(self):
        return self.nome
