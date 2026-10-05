from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


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
