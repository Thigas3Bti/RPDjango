from pathlib import Path

from django import forms

from .models import LocalPesca, MUNICIPIOS_RONDONIA


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        clean_one = super().clean
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [clean_one(upload, initial) for upload in files]


class LocalPescaForm(forms.ModelForm):
    fotos = MultipleFileField(
        label='Outras fotos do local (opcional)',
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
    )

    municipio = forms.ChoiceField(
        choices=[('', 'Selecione um município'), *MUNICIPIOS_RONDONIA],
        label='Município de Rondônia',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'municipios-rondonia',
            'placeholder': 'Digite para pesquisar um município',
            'autocomplete': 'off',
        }),
    )

    class Meta:
        model = LocalPesca
        fields = ('nome', 'municipio', 'descricao', 'foto', 'maps_url')
        labels = {
            'nome': 'Nome do local',
            'descricao': 'Descrição',
            'foto': 'Foto do local (opcional)',
            'maps_url': 'Link do Google Maps (opcional)',
        }
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: Rio Machado',
                'maxlength': 120,
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 2000,
                'placeholder': 'Conte o que os pescadores devem saber sobre o local.',
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'maps_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://maps.app.goo.gl/...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['maps_url'].required = True
        for field in self.fields.values():
            field.error_messages['required'] = 'Este campo é obrigatório.'
        self.fields['municipio'].error_messages['invalid_choice'] = (
            'Selecione um município válido de Rondônia.'
        )

    def clean_foto(self):
        return self._validar_imagem(self.cleaned_data.get('foto'))

    def clean_fotos(self):
        return [
            self._validar_imagem(foto)
            for foto in self.cleaned_data.get('fotos', [])
        ]

    @staticmethod
    def _validar_imagem(foto):
        if not foto:
            return foto
        if foto.size > 5 * 1024 * 1024:
            raise forms.ValidationError('A foto deve ter no máximo 5 MB.')

        tipos_por_extensao = {
            '.bmp': 'image/bmp',
            '.gif': 'image/gif',
            '.jpeg': 'image/jpeg',
            '.jpg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
        }
        extensao = Path(foto.name).suffix.lower()
        if foto.content_type != tipos_por_extensao.get(extensao):
            raise forms.ValidationError('Selecione um arquivo de imagem válido.')

        return foto


class InformacaoLocalForm(forms.Form):
    descricao = forms.CharField(
        label='Informações adicionais',
        max_length=2000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'maxlength': 2000,
            'placeholder': 'Compartilhe detalhes de acesso, estrutura, condições de pesca ou outros cuidados importantes.',
        }),
    )
    fotos = MultipleFileField(
        label='Fotos adicionais (opcional)',
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
    )

    def clean_fotos(self):
        return [
            LocalPescaForm._validar_imagem(foto)
            for foto in self.cleaned_data.get('fotos', [])
        ]
