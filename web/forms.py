from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nome de usuário'
        self.fields['username'].help_text = 'Informe o nome de usuário usado no cadastro.'
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Ex.: pescador123',
            'autocomplete': 'username',
        })
        self.fields['password'].label = 'Senha'
        self.fields['password'].help_text = 'Digite a senha da sua conta.'
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Digite sua senha',
            'autocomplete': 'current-password',
        })
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
    error_messages = {
        'password_mismatch': _('As senhas informadas não são iguais.'),
    }

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
        self.fields['username'].help_text = (
            'Escolha um nome de usuário para acessar sua conta.'
        )
        self.fields['first_name'].help_text = 'Informe seu primeiro nome.'
        self.fields['last_name'].help_text = 'Informe seu sobrenome.'
        self.fields['email'].help_text = 'Informe um e-mail válido para contato.'
        self.fields['password1'].help_text = (
            'Use pelo menos 8 caracteres. Evite senhas comuns e senhas formadas '
            'apenas por números.'
        )
        self.fields['password2'].help_text = 'Digite novamente a mesma senha.'
        placeholders = {
            'username': 'Ex.: pescador123',
            'first_name': 'Seu nome',
            'last_name': 'Seu sobrenome',
            'email': 'voce@exemplo.com',
            'password1': 'Crie uma senha',
            'password2': 'Repita sua senha',
        }
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.error_messages['required'] = _('Este campo é obrigatório.')
        for name, placeholder in placeholders.items():
            self.fields[name].widget.attrs['placeholder'] = placeholder
        self.fields['username'].widget.attrs['autocomplete'] = 'username'
        self.fields['first_name'].widget.attrs['autocomplete'] = 'given-name'
        self.fields['last_name'].widget.attrs['autocomplete'] = 'family-name'
        self.fields['email'].widget.attrs['autocomplete'] = 'email'
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'
