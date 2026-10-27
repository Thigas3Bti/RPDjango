from django import forms
from django.utils import timezone
from pathlib import Path

from .models import Comentario, EventoAgenda, Publicacao


MAX_PUBLICACAO_FOTO_SIZE = 5 * 1024 * 1024
PUBLICACAO_IMAGE_FORMATS = {
    '.bmp': 'BMP',
    '.gif': 'GIF',
    '.jpeg': 'JPEG',
    '.jpg': 'JPEG',
    '.png': 'PNG',
    '.webp': 'WEBP',
}


class PublicacaoImageField(forms.ImageField):
    def to_python(self, data):
        if data and data.size > MAX_PUBLICACAO_FOTO_SIZE:
            raise forms.ValidationError('A foto deve ter no máximo 5 MB.')
        return super().to_python(data)


class EventoAgendaForm(forms.ModelForm):
    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not usuario or not usuario.is_staff:
            self.fields['tipo'].choices = [
                choice for choice in self.fields['tipo'].choices
                if choice[0] != EventoAgenda.TIPO_OFICIAL
            ]

    class Meta:
        model = EventoAgenda
        fields = ['nome', 'tipo', 'data_evento', 'hora_evento', 'local', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: Campeonato de pesca',
                'maxlength': 100,
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'data_evento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'hora_evento': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade, rio ou ponto de encontro',
                'maxlength': 150,
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 5000,
                'placeholder': 'Conte os detalhes e o que os participantes precisam saber.',
            }),
        }

    def clean_data_evento(self):
        data_evento = self.cleaned_data['data_evento']
        if data_evento < timezone.localdate():
            raise forms.ValidationError('Escolha hoje ou uma data futura.')
        return data_evento


class PublicacaoForm(forms.ModelForm):
    foto = PublicacaoImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'community-photo-input',
            'accept': 'image/*',
            'aria-label': 'Selecionar foto para a publicação',
        }),
    )

    class Meta:
        model = Publicacao
        fields = ['titulo', 'texto', 'foto']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control community-field',
                'placeholder': 'Qual é o assunto da sua publicação?',
                'maxlength': 120,
            }),
            'texto': forms.Textarea(attrs={
                'class': 'form-control community-field',
                'rows': 6,
                'maxlength': 2000,
                'placeholder': 'Conte uma experiência, faça uma pergunta ou compartilhe uma dica...',
                'aria-describedby': 'publish-help',
            }),
        }

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if not foto:
            return foto

        extension = Path(foto.name).suffix.lower()
        if PUBLICACAO_IMAGE_FORMATS.get(extension) != foto.image.format:
            raise forms.ValidationError('Selecione um arquivo de imagem.')

        return foto

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('texto') and not cleaned_data.get('foto'):
            raise forms.ValidationError(
                'Escreva uma publicação ou selecione uma foto antes de publicar.'
            )
        return cleaned_data


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 500,
                'placeholder': 'Escreva um comentário...',
                'aria-label': 'Escreva um comentário',
            }),
        }
