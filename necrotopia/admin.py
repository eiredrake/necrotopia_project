import io
from datetime import datetime, timedelta
from typing import cast

import django.forms.models
import tagging
from django.contrib import admin
from django.contrib.admin.checks import InlineModelAdminChecks
from django.contrib.admin.helpers import ActionForm
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.timezone import make_aware
from imagekit.admin import AdminThumbnail
from nested_admin.nested import NestedModelAdmin, NestedTabularInline
from rolldice import rolldice
from pypdf import PdfReader, PdfWriter, PdfMerger
from tagging.forms import TagField
from tagging.models import TaggedItem, Tag, TagManager

from necrotopia.forms import RegisterUserForm
from necrotopia.models import UserProfile, Title, Gender, TimeUnits, \
    ResourceItem, RatedSkillItem, SkillRatings, SkillItem, SkillCategory, RulePicture, Rule, \
    ItemPicture, ModuleGrade, ModuleGradeResource, ModuleGradeSubAssembly, ModuleAssembly, ItemPdf, \
    Advertisement
from django import forms
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.utils.translation import gettext_lazy as _translate
from django.contrib import messages
from necrotopia.views import send_registration_email
from necrotopia_project.settings import GLOBAL_SITE_NAME
from functools import partial as curry


@admin.action(description='Set the tags of all selected items.')
def bulk_tagging(self, request, queryset):
    replace = False

    if 'replace' in request.POST:
        replace = request.POST.get('replace')

    if 'apply' in request.POST:
        new_tag_string = request.POST.get('new_tags')
        new_tags_list = tagging.models.parse_tag_input(new_tag_string)

        for tagged_item in queryset:
            Tag.objects.update_tags(tagged_item, None)
            if not replace:
                old_tags_list = tagging.models.parse_tag_input(tagged_item.tags)
                new_tags_list = list(set(new_tags_list) | set(old_tags_list))
                new_tag_string = ", ".join(new_tags_list)

            Tag.objects.update_tags(tagged_item, new_tags_list)
            tagged_item.tags = new_tag_string
            tagged_item.save()

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

    list_display = (
    'email', 'display_name', 'full_name', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'pronouns', 'gender')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Details', {
            'classes': ['collapse in'],
            'fields': ('title', 'full_name', 'display_name', 'pronouns', 'gender')}),
        ('Preferences', {
            'classes': ['collapse in'],
            'fields': ('display_game_advertisements',)}),
        ('Dates', {
            'classes': ['collapse in'],
            'fields': ('last_login', 'date_joined', 'birth_date',)}),
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


@admin.register(Title)
class TitleAdmin(NestedModelAdmin):
    list_display = ('descriptor',)
    list_display_links = list_display
    ordering = ('descriptor',)
    search_fields = ('descriptor',)


@admin.register(Gender)
class GenderAdmin(NestedModelAdmin):
    list_display = ('descriptor',)
    list_display_links = list_display
    ordering = ('descriptor',)
    search_fields = ('descriptor',)


class ResourceItemAdminForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width: 50em;'}))
    tags = TagField()


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
    list_display = ('name', 'expiration', 'tags')
    list_display_links = list_display
    ordering = ('name',)
    search_fields = ('name', 'tags')
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
    actions = [bulk_tagging]

    def expiration(self, obj):
        if obj.time_units != TimeUnits.No_Expiration:
            x = TimeUnits(obj.time_units).name
            return f'{obj.expiration_units} {x}'

    def get_changeform_initial_data(self, request):
        get_data = {'registrar': request.user.pk}
        return get_data


class SkillCategoryForm(forms.Form):
    categories = forms.ChoiceField(choices=SkillCategory.choices())


@admin.register(SkillItem)
class SkillItemAdmin(NestedModelAdmin):
    list_display = ('name', 'category', 'trunc_description', 'tags', )
    search_fields = ('name', 'category', 'tags')
    fieldsets = (
        (None,
         {
             'fields': ('name', 'category', 'tags' )
         }),
        ('Registrar', {
            'classes': ('collapse',),
            'fields': ('registrar', 'registry_date'),
        }),
    )
    inlines = [
        SkillRatingInline,
    ]

    def get_changeform_initial_data(self, request):
        get_data = {'registrar': request.user.pk}
        return get_data

    actions = ['set_skill_category', bulk_tagging]

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


class RulePictureInLine(NestedTabularInline):
    model = RulePicture
    extra = 0
    fields = ('picture', 'image_preview')
    readonly_fields = ('image_preview',)


class RuleAdminForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = '__all__'
        widgets = {
            'text': forms.Textarea(attrs={'rows': 10, 'cols': '100'})
        }


@admin.register(Rule)
class RuleAdmin(NestedModelAdmin):
    list_display = ('name', 'partial_slug', 'reference', 'tags')
    list_display_links = list_display
    inlines = [
        RulePictureInLine,
    ]
    form = RuleAdminForm
    fieldsets = (
        (None,
         {
             'fields': ('name', 'reference', 'slug', 'text', 'tags')
         }),
        ('Creator', {
            'classes': ('collapse',),
            'fields': ('creator', 'creation_date'),
        }),
    )

    actions = [bulk_tagging]


    def get_changeform_initial_data(self, request):
        get_data = {'creator': request.user.pk}
        return get_data

    def images(self, obj):
        if obj.pictures is not None:
            return obj.pictures.count()


class ItemPdfInLine(NestedTabularInline):
    model = ItemPdf
    extra = 0
    fields = ('pdf',)


class ItemPictureInLine(NestedTabularInline):
    model = ItemPicture
    extra = 0
    fields = ('picture', 'image_preview')
    readonly_fields = ('image_preview',)


class ModuleResourceInline(NestedTabularInline):
    extra = 0
    model = ModuleGradeResource
    fields = ('quantity', 'resource')


class ModuleSubAssemblyInLine(NestedTabularInline):
    extra = 0
    model = ModuleGradeSubAssembly
    fields = ('quantity', 'grade', 'assembly')


class ModuleGradeInline(NestedTabularInline):
    extra = 0
    max_num = 3
    model = ModuleGrade
    fields = ('grade', 'name', 'mind', 'time', 'mechanics')
    inlines = [
        ModuleResourceInline,
        ModuleSubAssemblyInLine,
    ]


@admin.register(ModuleAssembly)
class ModuleAssemblyAdmin(NestedModelAdmin):
    actions = ['print_pdfs', bulk_tagging]
    list_display = (
    'name', 'item_type', 'checked', 'published', 'has_image', 'has_pdf', 'last_update_date', 'expiration', 'tags')
    list_display_links = list_display
    ordering = ('name',)
    search_fields = ('name', 'published', 'checked', )
    inlines = [
        ItemPictureInLine,
        ItemPdfInLine,
        ModuleGradeInline,
    ]
    fieldsets = (
        (None,
         {
             'fields':
                 (
                     'name',
                     'expiration_units',
                     'time_units',
                     'item_type',
                     'details',
                     'visual_description',
                     'published',
                     'checked',
                     'achievement_mechanics',
                     'print_duplication',
                     'tags',
                     'usage_tree',
                 )
         }),
        ('Crafting and Usage', {
            'classes': ('collapse',),
            'fields': ('crafting_tree', 'crafting_area', ),
        }),
        ('Registrar', {
            'classes': ('collapse',),
            'fields': ('registrar', 'registration_date', 'last_update_date'),
        }),
    )

    @admin.action(description="Print the PDFs of all selected items")
    def print_pdfs(self, request, queryset):
        if 'proceed' in request.POST:
            output_file = PdfWriter()
            try:
                for item in queryset:
                    for module_pdf in ItemPdf.objects.filter(pdf_assembly_item_id=item.pk):
                        reader = PdfReader(module_pdf.pdf.open("rb"))
                        number_of_pages = len(reader.pages)
                        for page_number in range(number_of_pages):
                            page = reader.pages[page_number]
                            output_file.add_page(page)

                with io.BytesIO() as pdf:
                    output_file.write(pdf)
                    response = HttpResponse(pdf.getbuffer(), content_type='application/pdf')
                    response['Content-Disposition'] = 'filename=%s' % 'output.pdf'
                    return response
            finally:
                output_file.close()

        elif 'cancel' in request.POST:
            self.message_user(request, level=messages.ERROR, message="Action cancelled")
            return HttpResponseRedirect(request.get_full_path())
        else:
            return render(request, 'necrotopia/admin_print_pdfs.html', context={
                "title": 'Confirm Action',
                "items": queryset,
            })

    @admin.display(description='Has image', boolean=True)
    def has_image(self, obj: ModuleAssembly) -> bool:
        return obj.has_image()

    @admin.display(description='Has PDF', boolean=True)
    def has_pdf(self, obj: ModuleAssembly) -> bool:
        return obj.has_pdf()

    def save_model(self, request, obj, form, change):
        obj.last_update_date = make_aware(datetime.now())
        obj.save()

    def expiration(self, obj):
        if obj.time_units != TimeUnits.No_Expiration:
            x = TimeUnits(obj.time_units).name
            return f'{obj.expiration_units} {x}'

    def get_changeform_initial_data(self, request):
        get_data = super(ModuleAssemblyAdmin, self).get_changeform_initial_data(request)
        get_data['registrar'] = request.user.pk
        return get_data

    def get_form(self, request, obj=None, **kwargs):
        form = super(ModuleAssemblyAdmin, self).get_form(request, obj, **kwargs)

        if 'name' in form.base_fields:
            form.base_fields['name'].widget.attrs['style'] = 'width: 45em;'

        if 'achievement_mechanics' in form.base_fields:
            form.base_fields['achievement_mechanics'].widget = Textarea()
            form.base_fields['achievement_mechanics'].widget.attrs['style'] = 'width: 45em; height: 3em;'

        if 'print_duplication' in form.base_fields:
            form.base_fields['print_duplication'].widget.attrs['style'] = 'width: 45em;'

        if 'tags' in form.base_fields:
            form.base_fields['tags'].widget = Textarea()
            form.base_fields['tags'].widget.attrs['style'] = 'width: 45em; height: 3em;'

        if 'details' in form.base_fields:
            form.base_fields['details'].widget = Textarea()
            form.base_fields['details'].widget.attrs['style'] = 'width: 45em; height: 5em;'

        if 'visual_description' in form.base_fields:
            form.base_fields['visual_description'].widget = Textarea()
            form.base_fields['visual_description'].widget.attrs['style'] = 'width: 45em; height: 5em;'

        return form


@admin.register(Advertisement)
class AdvertisementCarouselAdmin(admin.ModelAdmin):
    list_display = ('name', 'published', 'is_active', 'start_date', 'end_date')
    list_display_links = ('name',)

    fieldsets = (
        (None,
         {
             'fields': ('name', 'slug', 'link', 'image', 'published', 'start_date', 'end_date', )
         }),
        ('Registrar', {
            'classes': ('collapse',),
            'fields': ('registrar', 'registry_date',),
        }),
    )

    class Meta:
        model = Advertisement

    @admin.display(description='Currently Active', boolean=True)
    def is_active(self, obj: Advertisement) -> bool:
        return obj.is_active()

    def get_changeform_initial_data(self, request):
        get_data = super(AdvertisementCarouselAdmin, self).get_changeform_initial_data(request)
        get_data['registrar'] = request.user.pk
        get_data['end_date'] = timezone.now() + + timedelta(days=30)
        return get_data
