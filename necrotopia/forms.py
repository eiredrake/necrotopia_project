from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core import serializers
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _translate
from django_password_validators.password_character_requirements.password_validation import PasswordCharacterValidator
from django_password_validators.password_history.models import PasswordHistory
from django_password_validators.password_history.password_validation import UniquePasswordsValidator

from necrotopia.models import UserProfile


class AuthenticateUserForm(AuthenticationForm):
    remember_me = forms.BooleanField(label=_translate('Remember Me'), initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-loginForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'authenticate_user'
        self.helper.error_text_inline = True

        self.helper.add_input(Submit('submit', 'Login'))


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label=_translate('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_translate('Confirm Password'), widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ('email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = UserProfile.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError(_translate('This username already exists'))

        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 is not None and password1 != password2:
            self.add_error('password2', _translate('Your passwords must match'))

        return cleaned_data


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = UserProfile
        fields = ('email',)
