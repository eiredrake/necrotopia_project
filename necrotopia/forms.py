from crispy_forms.bootstrap import StrictButton, InlineField, FormActions, UneditableField, FieldWithButtons, \
    PrependedText, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, Div, ButtonHolder, HTML, Button
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, BaseUserCreationForm, \
    UsernameField
from django.core import serializers
from django.core.validators import EmailValidator
from django.urls import reverse
from django.utils.safestring import mark_safe
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
    display_name = forms.CharField(label=_translate('Display Name'), widget=forms.TextInput, required=True)

    class Meta:
        model = UserProfile
        fields = ('display_name', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-user_profile_form'
        self.helper.form_method = 'post'
        self.helper.form_action = 'user_profile_change'
        # self.helper.form_show_labels = False
        # self.helper.form_class = 'form-inline'
        # self.helper.label_class = 'col'
        # self.helper.field_class = 'col'
        self.helper.error_text_inline = True
        self.helper.layout = Layout(
            Field('display_name'),
            # HTML('<button type="cancel" class="btn float-right mb-2"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg></button>'),
            # HTML('<button type="submit" class="btn btn-success float-right mb-2"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check2-circle" viewBox="0 0 16 16"><path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0z"/><path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l7-7z"/></svg></button>'),
        )

        # self.helper.add_input(Button('cancel', 'Cancel', css_class='float-right mb-2', onclick="window.location.href = '{}';".format(reverse('home'))))
        # self.helper.add_input(Submit('submit', css_class='float-right mb-2', value='Fuck'))


