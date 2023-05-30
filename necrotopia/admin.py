from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from necrotopia.forms import RegisterUserForm
from necrotopia.models import UserProfile
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.utils.translation import gettext_lazy as _translate
from django.contrib import messages
from necrotopia.views import send_registration_email
from necrotopia_project.settings import GLOBAL_SITE_NAME


def deactivate_user(modeladmin, request, queryset):
    deactivate_user.short_description = 'Deactivate user'

    queryset.update(is_active=False)


def resend_registration_email(modeladmin, request, queryset):
    resend_registration_email.short_description = 'Resend Activation Email'

    queryset.update(is_active=False)
    for user in queryset:
        send_registration_email(request, user)

    messages.success(request, _translate('Registration email resent'))


class CustomUserAdmin(UserAdmin):
    add_form = RegisterUserForm
    change_form = RegisterUserForm

    model = UserProfile

    list_display = ('email', 'is_active', 'is_staff', 'is_superuser', 'last_login',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active',
                                    'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    actions = [deactivate_user, resend_registration_email]


admin.site.register(UserProfile, CustomUserAdmin)


class Group(DjangoGroup):
    """Instead of trying to get new user under existing `Aunthentication and Authorization`
    banner, create a proxy group model under our Accounts app label.
    Refer to: https://github.com/tmm/django-username-email/blob/master/cuser/admin.py
    """

    class Meta:
        verbose_name = _translate('group')
        verbose_name_plural = _translate('groups')
        proxy = True


admin.site.unregister(DjangoGroup)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass
