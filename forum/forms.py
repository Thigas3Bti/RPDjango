from django import forms
from pathlib import Path

from .models import Comentario, Publicacao


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
