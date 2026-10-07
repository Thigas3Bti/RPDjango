from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Dica


class DicaForm(forms.ModelForm):
    class Meta:
        model = Dica
        fields = ['titulo', 'nivel', 'descricao']
        labels = {
            'titulo': 'Título da dica',
            'nivel': 'Nível de experiência',
            'descricao': 'Descrição da dica',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 120,
                'placeholder': 'Ex.: Como escolher a isca para o local',
            }),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Explique sua dica com detalhes e contexto.',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.error_messages['required'] = _('Este campo é obrigatório.')


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuário'
        self.fields['password'].label = 'Senha'
        for field in self.fields.values():
            field.error_messages['required'] = _('Este campo é obrigatório.')
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        try:
            return super().clean()
        except ValidationError as error:
            if not any(item.code == 'invalid_login' for item in error.error_list):
                raise

            username = self.cleaned_data.get('username')
            user_model = get_user_model()
            user_exists = username and user_model._default_manager.filter(
                **{user_model.USERNAME_FIELD: username}
            ).exists()
            message = (
                _('Senha incorreta.')
                if user_exists
                else _('Usuário não encontrado.')
            )
            raise ValidationError(message, code='invalid_login')


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nome de usuário'
        self.fields['first_name'].label = 'Nome'
        self.fields['last_name'].label = 'Sobrenome'
        self.fields['email'].label = 'E-mail'
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirme a senha'
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
