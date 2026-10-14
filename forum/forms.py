from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from django import forms
from django.utils import timezone

from .models import Comentario, EventoAgenda, Publicacao


class _IframeSrcParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'iframe':
            source = dict(attrs).get('src')
            if source:
                self.sources.append(source)


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
        fields = [
            'nome', 'tipo', 'data_evento', 'hora_evento', 'local', 'mapa_url',
            'descricao',
        ]
        field_classes = {'mapa_url': forms.CharField}
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
            'mapa_url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cole a URL ou o código iframe de incorporação',
                'maxlength': 1000,
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

    def clean_mapa_url(self):
        mapa_url = self.cleaned_data.get('mapa_url', '').strip()
        if not mapa_url:
            return ''

        if '<' in mapa_url:
            parser = _IframeSrcParser()
            parser.feed(mapa_url)
            if len(parser.sources) != 1:
                raise forms.ValidationError(
                    'Cole uma URL de incorporação do Google Maps ou um único iframe.'
                )
            mapa_url = parser.sources[0].strip()

        partes_url = urlsplit(mapa_url)
        if (
            partes_url.scheme != 'https'
            or partes_url.hostname not in {'google.com', 'www.google.com'}
            or partes_url.path != '/maps/embed'
        ):
            raise forms.ValidationError(
                'Use uma URL de incorporação segura do Google Maps.'
            )

        return mapa_url


class PublicacaoForm(forms.ModelForm):
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
            'foto': forms.FileInput(attrs={
                'class': 'community-photo-input',
                'accept': 'image/*',
                'aria-label': 'Selecionar foto para a publicação',
            }),
        }

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if not foto:
            return foto

        if foto.size > 5 * 1024 * 1024:
            raise forms.ValidationError('A foto deve ter no máximo 5 MB.')
        image_types = {
            '.bmp': 'image/bmp',
            '.gif': 'image/gif',
            '.jpeg': 'image/jpeg',
            '.jpg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
        }
        extension = Path(foto.name).suffix.lower()
        if foto.content_type != image_types.get(extension):
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
