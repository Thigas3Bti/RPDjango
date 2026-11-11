from django.conf import settings
from django.db import models


class Equipamento(models.Model):
    CATEGORIAS = [
        ('vara', 'Vara'),
        ('linha', 'Linha'),
        ('anzol', 'Anzol'),
        ('molinete', 'Molinete / carretilha'),
        ('isca', 'Isca'),
        ('seguranca', 'Segurança'),
        ('acessorio', 'Acessório'),
        ('outro', 'Outro'),
    ]

    nome = models.CharField('Nome do equipamento', max_length=120)
    categoria = models.CharField('Categoria', max_length=30, choices=CATEGORIAS, default='outro')
    foto = models.ImageField('Foto do equipamento', upload_to='equipamentos/', blank=False, null=True)
    descricao = models.TextField('Descrição')
    uso = models.TextField('Uso recomendado', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['categoria', 'nome']
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'

    def __str__(self):
        return self.nome


class FotoAdicionalEquipamento(models.Model):
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.CASCADE,
        related_name='fotos_adicionais',
    )
    foto = models.ImageField('Foto adicional', upload_to='equipamentos/')

    class Meta:
        verbose_name = 'Foto adicional de equipamento'
        verbose_name_plural = 'Fotos adicionais de equipamentos'

    def __str__(self):
        return f'Foto de {self.equipamento.nome}'


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


class SolicitacaoRedefinicaoSenha(models.Model):
    usuario = models.CharField(max_length=150)
    email = models.EmailField()
    senha_solicitada = models.CharField(
        max_length=256,
        blank=True,
        default='',
        editable=False,
    )
    criada_em = models.DateTimeField(auto_now_add=True)
    atendida_em = models.DateTimeField(blank=True, null=True)
    atendida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='solicitacoes_senha_atendidas',
    )

    class Meta:
        ordering = ['atendida_em', '-criada_em']
        verbose_name = 'Solicitação de redefinição de senha'
        verbose_name_plural = 'Solicitações de redefinição de senha'

    def __str__(self):
        return f'{self.usuario} ({self.email})'
