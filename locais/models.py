from django.db import models
from django.conf import settings


MUNICIPIOS_RONDONIA = [
    ("Alta Floresta d'Oeste", "Alta Floresta d'Oeste"),
    ('Alto Alegre dos Parecis', 'Alto Alegre dos Parecis'),
    ('Alto Paraíso', 'Alto Paraíso'),
    ("Alvorada d'Oeste", "Alvorada d'Oeste"),
    ('Ariquemes', 'Ariquemes'),
    ('Buritis', 'Buritis'),
    ('Cabixi', 'Cabixi'),
    ('Cacaulândia', 'Cacaulândia'),
    ('Cacoal', 'Cacoal'),
    ('Campo Novo de Rondônia', 'Campo Novo de Rondônia'),
    ('Candeias do Jamari', 'Candeias do Jamari'),
    ('Castanheiras', 'Castanheiras'),
    ('Cerejeiras', 'Cerejeiras'),
    ('Chupinguaia', 'Chupinguaia'),
    ('Colorado do Oeste', 'Colorado do Oeste'),
    ('Corumbiara', 'Corumbiara'),
    ('Costa Marques', 'Costa Marques'),
    ('Cujubim', 'Cujubim'),
    ("Espigão d'Oeste", "Espigão d'Oeste"),
    ('Governador Jorge Teixeira', 'Governador Jorge Teixeira'),
    ('Guajará-Mirim', 'Guajará-Mirim'),
    ('Itapuã do Oeste', 'Itapuã do Oeste'),
    ('Jaru', 'Jaru'),
    ('Ji-Paraná', 'Ji-Paraná'),
    ("Machadinho d'Oeste", "Machadinho d'Oeste"),
    ('Ministro Andreazza', 'Ministro Andreazza'),
    ('Mirante da Serra', 'Mirante da Serra'),
    ('Monte Negro', 'Monte Negro'),
    ("Nova Brasilândia d'Oeste", "Nova Brasilândia d'Oeste"),
    ('Nova Mamoré', 'Nova Mamoré'),
    ('Nova União', 'Nova União'),
    ('Novo Horizonte do Oeste', 'Novo Horizonte do Oeste'),
    ('Ouro Preto do Oeste', 'Ouro Preto do Oeste'),
    ('Parecis', 'Parecis'),
    ('Pimenta Bueno', 'Pimenta Bueno'),
    ('Pimenteiras do Oeste', 'Pimenteiras do Oeste'),
    ('Porto Velho', 'Porto Velho'),
    ('Presidente Médici', 'Presidente Médici'),
    ('Primavera de Rondônia', 'Primavera de Rondônia'),
    ('Rio Crespo', 'Rio Crespo'),
    ('Rolim de Moura', 'Rolim de Moura'),
    ("Santa Luzia d'Oeste", "Santa Luzia d'Oeste"),
    ("São Felipe d'Oeste", "São Felipe d'Oeste"),
    ('São Francisco do Guaporé', 'São Francisco do Guaporé'),
    ('São Miguel do Guaporé', 'São Miguel do Guaporé'),
    ('Seringueiras', 'Seringueiras'),
    ('Teixeirópolis', 'Teixeirópolis'),
    ('Theobroma', 'Theobroma'),
    ('Urupá', 'Urupá'),
    ('Vale do Anari', 'Vale do Anari'),
    ('Vale do Paraíso', 'Vale do Paraíso'),
    ('Vilhena', 'Vilhena'),
]


class LocalPesca(models.Model):
    nome = models.CharField(max_length=120)
    municipio = models.CharField(
        max_length=120,
        choices=MUNICIPIOS_RONDONIA,
        blank=True,
    )
    descricao = models.TextField(max_length=2000)
    imagem_url = models.URLField('URL da imagem', blank=True)
    foto = models.FileField(
        'Foto do local',
        upload_to='locais/%Y/%m/',
        blank=True,
    )
    maps_url = models.URLField('Link do Google Maps', blank=True)
    cadastrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='locais_de_pesca_cadastrados',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Local de pesca'
        verbose_name_plural = 'Locais de pesca'

    def __str__(self):
        return self.nome


class FotoLocal(models.Model):
    local = models.ForeignKey(
        LocalPesca,
        on_delete=models.CASCADE,
        related_name='fotos',
    )
    informacao = models.ForeignKey(
        'InformacaoLocal',
        on_delete=models.CASCADE,
        related_name='fotos',
        null=True,
        blank=True,
    )
    arquivo = models.FileField(upload_to='locais/%Y/%m/galeria/')
    adicionada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['adicionada_em', 'pk']
        verbose_name = 'Foto do local'
        verbose_name_plural = 'Fotos do local'

    def __str__(self):
        return f'Foto de {self.local.nome}'


class InformacaoLocal(models.Model):
    local = models.ForeignKey(
        LocalPesca,
        on_delete=models.CASCADE,
        related_name='informacoes_adicionais',
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='informacoes_locais_compartilhadas',
    )
    descricao = models.TextField(max_length=2000)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em', '-pk']
        verbose_name = 'Informação adicional do local'
        verbose_name_plural = 'Informações adicionais do local'

    def __str__(self):
        return f'Informação de {self.local.nome}'
