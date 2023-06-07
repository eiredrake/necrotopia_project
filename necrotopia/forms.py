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

from necrotopia.models import UserProfile, Title, Gender, UsefulLinks


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
    email_validator = EmailValidator()
    display_name = forms.CharField(label=_translate('Display Name'), widget=forms.TextInput, required=True,)
    full_name = forms.CharField(label=_translate("Full Name"), widget=forms.TextInput, required=False)

    class Meta:
        model = UserProfile
        fields = ('display_name', 'full_name', 'title', 'gender', )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-user_profile_form'
        self.helper.form_method = 'post'
        self.helper.form_action = 'user_profile_change'
        self.helper.form_show_labels = True
        self.helper.error_text_inline = True

        super(UserProfileForm, self).__init__(*args, **kwargs)
        # self.fields["gender"].choices = [(item.id, item.descriptor) for item in Gender.objects.all()]
        # self.fields["title"].choices = [(item.id, item.descriptor) for item in Title.objects.all()]
