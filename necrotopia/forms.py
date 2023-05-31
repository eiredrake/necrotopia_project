from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, BaseUserCreationForm, \
    UsernameField
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


class RegisterUserForm(BaseUserCreationForm):
    email = forms.EmailField(label=_translate('Email'), widget=forms.EmailInput, required=True, validators=[EmailValidator])
    email_2 = forms.EmailField(label=_translate('Email Confirmation'), widget=forms.EmailInput, required=True, validators=[EmailValidator])

    class Meta:
        model = UserProfile
        fields = ("email", 'email_2')
        field_classes = {"email": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-registerForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'register_user'
        self.helper.error_text_inline = True

        self.helper.add_input(Submit('submit', 'Register', css_class='bg-success float-right pb-2'))


class UserProfileForm(forms.ModelForm):
    display_name = forms.CharField(label=_translate('Display Name'), widget=forms.TextInput)
    full_name = forms.CharField(label=_translate('Full Name'), widget=forms.TextInput, required=True)

    class Meta:
        model = UserProfile
        fields = ('display_name', 'title', 'full_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-userProfile'
        self.helper.form_method = 'post'
        self.helper.form_action = 'user_profile_change'
        self.helper.error_text_inline = True

        self.helper.add_input(Submit('cancel', 'Cancel', css_class='bg-danger float-right pb-2 m-2'))
        self.helper.add_input(Submit('submit', 'Update', css_class='bg-success float-right pb-2 m-2'))

