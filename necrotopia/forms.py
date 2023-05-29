from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _translate

from necrotopia.models import UserProfile


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(label=_translate('Remember Me'), initial=False, required=False)


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = UserProfile
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = UserProfile
        fields = ('email',)

