from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from nested_admin.nested import NestedModelAdmin

from necrotopia.forms import RegisterUserForm
from necrotopia.models import UserProfile, Pronoun, Title
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

    list_display = ('email', 'display_name', 'full_name', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'get_user_pronouns')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Details', {
            'classes': ['collapse in'],
            'fields': ('title', 'full_name', 'display_name', 'pronouns', )}),
        ('Dates', {
            'classes': ['collapse in'],
            'fields': ('last_login', 'date_joined', 'birth_date', )}),
        ('Permissions', {
            'classes': ['collapse in'],
            'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
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

    def get_user_pronouns(self, obj: UserProfile):
        if obj.pronouns is None:
            return "Not Set"
        else:
            return obj.pronouns.object

    get_user_pronouns.short_description = _translate('Pronouns')


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


admin.site.register(Pronoun)
admin.site.register(Title)
