import django.forms.models
from django.contrib import admin
from django.contrib.admin.checks import InlineModelAdminChecks
from django.contrib.admin.helpers import ActionForm
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect
from django.shortcuts import render
from nested_admin.nested import NestedModelAdmin, NestedTabularInline
from taggit.forms import TagField, TextareaTagWidget

from necrotopia.forms import RegisterUserForm
from necrotopia.models import UserProfile, Title, ChapterStaffType, Chapter, Gender, UsefulLinks, TimeUnits, \
    ResourceItem, RatedSkillItem, SkillRatings, SkillItem, ChapterStaff, Department, SkillCategory
from django import forms
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.utils.translation import gettext_lazy as _translate
from django.contrib import messages
from necrotopia.views import send_registration_email
from necrotopia_project.settings import GLOBAL_SITE_NAME
from taggit.forms import TagField
from taggit.managers import TaggableManager
from taggit.models import Tag
from functools import partial as curry


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

    list_display = ('email', 'display_name', 'full_name', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'pronouns', 'gender')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Details', {
            'classes': ['collapse in'],
            'fields': ('title', 'full_name', 'display_name', 'pronouns', 'gender' )}),
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


@admin.register(ChapterStaffType)
class ChapterStaffTypeAdmin(BaseGroupAdmin):
    list_display = ('name', 'description', 'registry_date', 'registrar')
    list_display_links = list_display
    ordering = ('name', )
    search_fields = ('name', )
    filter_horizontal = ()


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass


@admin.register(Title)
class TitleAdmin(NestedModelAdmin):
    list_display = ('descriptor', )
    list_display_links = list_display
    ordering = ('descriptor', )
    search_fields = ('descriptor', )


@admin.register(Gender)
class GenderAdmin(NestedModelAdmin):
    list_display = ('descriptor', )
    list_display_links = list_display
    ordering = ('descriptor', )
    search_fields = ('descriptor', )


class UsefulLinksInline(NestedTabularInline):
    extra = 0
    model = UsefulLinks
    fields = ('name', 'published', 'url')
    classes = ('collapse', )


class ChapterStaffInline(NestedTabularInline):
    extra = 0
    model = ChapterStaff
    fields = ('user_profile', 'department', 'type')
    classes = ('collapse', )

    verbose_name = "Chapter Staff Member"
    verbose_name_plural = "Chapter Staff"


@admin.register(Department)
class DepartmentAdmin(NestedModelAdmin):
    list_display = ('name', 'description', 'registry_date', 'registrar')
    list_display_links = list_display
    ordering = ('name', )
    search_fields = ('name', )

    def get_changeform_initial_data(self, request):
        get_data = {'registrar': request.user.pk}
        return get_data


@admin.register(Chapter)
class ChapterAdmin(NestedModelAdmin):
    list_display = ('name', 'active', 'registry_date', 'registrar')
    list_display_links = list_display
    ordering = ('name', )
    search_fields = ('name', )

    fieldsets = (
        (None,
         {
             'fields': ('name', 'active', )
         }),
        ('Registrar', {
            'classes': ('collapse',),
            'fields': ('registrar', 'registry_date'),
        }),
    )

    inlines = [
        UsefulLinksInline,
        ChapterStaffInline,
    ]

    def get_changeform_initial_data(self, request):
        get_data = super(ChapterAdmin, self).get_changeform_initial_data(request)
        get_data['registrar'] = request.user.pk
        return get_data


@admin.register(UsefulLinks)
class UsefulLinksAdmin(NestedModelAdmin):
    list_display = ('name', 'chapter_link', 'url', 'published', 'registrar', 'registry_date')
    list_display_links = list_display
    ordering = ('name', )
    search_fields = ('name', )


class ResourceItemAdminForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width: 50em;'}))
    tags = TagField(widget=TextareaTagWidget(attrs={'style': 'width: 50em'}))


class RatedSkillInline(NestedTabularInline):
    extra = 0
    model = RatedSkillItem
    fields = ('mind', 'time', 'grade', 'skill', 'one_use_per_game')


class SkillRatingInline(NestedTabularInline):
    extra = 0
    model = SkillRatings
    fields = ('grade', 'description')
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': '20', 'cols': '80'})},
    }


@admin.register(ResourceItem)
class ResourceItemAdmin(NestedModelAdmin):
    form = ResourceItemAdminForm
    tag_display = ['tag_list']
    # fields = ('name', 'expiration_units', 'time_units', 'tags', 'registrar', 'registry_date')
    list_display = ('name', 'expiration', 'related_skills', 'tag_list')
    list_display_links = list_display
    ordering = ('name',)
    search_fields = ('name', 'tags__name', 'ratedskillitem__skill__name')
    inlines = [
        # RatedSkillInline,
    ]
    fieldsets = (
        (None,
         {
             'fields': ('name', 'expiration_units', 'time_units', 'tags')
         }),
        ('Registration', {
            'classes': ('collapse',),
            'fields': ('registrar', 'registry_date'),
        }),
    )
    actions = ['bulk_tagging']

    @admin.action(description='Set the tags of all selected items.')
    def bulk_tagging(self, request, queryset):
        # print("post: %s" % request.POST)
        replace = False

        if 'replace' in request.POST:
            replace = request.POST.get('replace')

        # print('replace: %s' % str(replace))

        if 'apply' in request.POST:
            new_tags = request.POST.get('new_tags')
            new_tags = new_tags.split(',')

            for item in queryset:
                old_tags = list(item.tags.all())
                if not replace:
                    new_tags = new_tags + old_tags

                item.tags.set(tags=new_tags, through_defaults=None, clear=False)

            self.message_user(request, level=messages.SUCCESS,
                              message="Changed tags on {} items".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())
        elif 'cancel' in request.POST:
            self.message_user(request, level=messages.ERROR, message="Action cancelled")
            return HttpResponseRedirect(request.get_full_path())
        else:

            return render(request, 'necrotopia/bulk_tagging.html', context={
                "title": 'Confirm Action',
                "items": queryset,
            })

    def related_skills(self, obj):
        if obj.ratedskillitem_set is not None:
            the_skills = obj.ratedskillitem_set.all().order_by('grade', 'skill__name', )
            return u", ".join(str(o) for o in the_skills)
        else:
            return dir(obj)

    def expiration(self, obj):
        if obj.time_units != TimeUnits.No_Expiration:
            x = TimeUnits(obj.time_units).name
            return f'{obj.expiration_units} {x}'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        the_tags = obj.tags.all().order_by('name')
        return u", ".join(o.name for o in the_tags)

    def get_changeform_initial_data(self, request):
        get_data = {'registrar': request.user.pk}
        return get_data


class SkillCategoryForm(forms.Form):
    categories = forms.ChoiceField(choices=SkillCategory.choices())


@admin.register(SkillItem)
class SkillItemAdmin(NestedModelAdmin):
    tag_display = ['tag_list']
    list_display = ('name', 'category', 'trunc_description', 'tag_list')
    search_fields = ('name', 'category', 'tags__name')
    fieldsets = (
        (None,
         {
             'fields': ('name', 'category', 'tags')
         }),
        ('Registrar', {
            'classes': ('collapse',),
            'fields': ('registrar', 'registry_date'),
        }),
    )
    inlines = [
        SkillRatingInline,
    ]

    def tag_list(self, obj):
        the_tags = obj.tags.all().order_by('name')
        return u", ".join(o.name for o in the_tags)

    def get_changeform_initial_data(self, request):
        get_data = {'registrar': request.user.pk}
        return get_data

    actions = ['set_skill_category']

    def set_skill_category(self, request, queryset):
        if 'do_action' in request.POST:
            form = SkillCategoryForm(request.POST)
            if form.is_valid():
                category = SkillCategory(int(form.cleaned_data['categories']))
                updated = queryset.update(category=category)
                messages.success(request, '{0} records were updated'.format(updated))
                return
        else:
            form = SkillCategoryForm()

        return render(request, 'necrotopia/skill_category_selector.html',
                      {'title': u'Choose new category',
                       'objects': queryset,
                       'form': form,
                       'categories': SkillCategory.choices()})

    set_skill_category.short_description = 'Change Category'
