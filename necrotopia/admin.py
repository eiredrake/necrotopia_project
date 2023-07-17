import io
from datetime import datetime

import django.forms.models
from django.contrib import admin
from django.contrib.admin.checks import InlineModelAdminChecks
from django.contrib.admin.helpers import ActionForm
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.timezone import make_aware
from imagekit.admin import AdminThumbnail
from nested_admin.nested import NestedModelAdmin, NestedTabularInline
from rolldice import rolldice
from taggit.forms import TagField, TextareaTagWidget
from pypdf import PdfReader, PdfWriter, PdfMerger

from necrotopia.forms import RegisterUserForm, FinancialInvestmentAddForm
from necrotopia.models import UserProfile, Title, ChapterStaffType, Chapter, Gender, UsefulLinks, TimeUnits, \
    ResourceItem, RatedSkillItem, SkillRatings, SkillItem, ChapterStaff, Department, SkillCategory, RulePicture, Rule, \
    ItemPicture, ModuleGrade, ModuleGradeResource, ModuleGradeSubAssembly, ModuleAssembly, ItemPdf, \
    FinancialInstitution, FinancialInvestment, InvestmentResult, FinancialInstitutionModifier, ChapterPicture, \
    InstitutionPicture, Advertisement
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


class ChapterPictureInLine(NestedTabularInline):
    model = ChapterPicture
    extra = 0
    fields = ('picture', 'image_preview')
    readonly_fields = ('image_preview',)


class FinancialInstitutionPictureInLine(NestedTabularInline):
    model = InstitutionPicture
    extra = 0
    fields = ('picture', 'image_preview')
    readonly_fields = ('image_preview',)


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


@admin.register(ChapterStaffType)
class ChapterStaffTypeAdmin(BaseGroupAdmin):
    list_display = ('name', 'description', 'registry_date', 'registrar')
    list_display_links = list_display
    ordering = ('name',)
    search_fields = ('name',)
    filter_horizontal = ()


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass


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


class UsefulLinksInline(NestedTabularInline):
    extra = 0
    model = UsefulLinks
    fields = ('name', 'published', 'url')
    classes = ('collapse',)


class ChapterStaffInline(NestedTabularInline):
    extra = 0
    model = ChapterStaff
    fields = ('user_profile', 'department', 'type')
    classes = ('collapse',)

    verbose_name = "Chapter Staff Member"
    verbose_name_plural = "Chapter Staff"


@admin.register(Department)
class DepartmentAdmin(NestedModelAdmin):
    list_display = ('name', 'description', 'registry_date', 'registrar')
    list_display_links = list_display
    ordering = ('name',)
    search_fields = ('name',)

    def get_changeform_initial_data(self, request):
        get_data = {'registrar': request.user.pk}
        return get_data


@admin.register(Chapter)
class ChapterAdmin(NestedModelAdmin):
    list_display = ('name', 'active', 'registry_date', 'registrar')
    list_display_links = list_display
    ordering = ('name',)
    search_fields = ('name',)

    fieldsets = (
        (None,
         {
             'fields': ('name', 'active', 'chapter_pictures')
         }),
        ('Registrar', {
            'classes': ('collapse',),
            'fields': ('registrar', 'registry_date'),
        }),
    )

    inlines = [
        UsefulLinksInline,
        ChapterStaffInline,
        ChapterPictureInLine,
    ]

    def get_changeform_initial_data(self, request):
        get_data = super(ChapterAdmin, self).get_changeform_initial_data(request)
        get_data['registrar'] = request.user.pk
        return get_data


@admin.register(UsefulLinks)
class UsefulLinksAdmin(NestedModelAdmin):
    list_display = ('name', 'chapter_link', 'url', 'published', 'registrar', 'registry_date')
    list_display_links = list_display
    ordering = ('name',)
    search_fields = ('name',)


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
    tag_display = ['tag_list']
    list_display = ('name', 'partial_slug', 'reference', 'tag_list')
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

    def get_changeform_initial_data(self, request):
        get_data = {'creator': request.user.pk}
        return get_data

    def tag_list(self, obj):
        the_tags = obj.tags.all().order_by('name')
        return u", ".join(o.name for o in the_tags)

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
    tag_display = ['tag_list']
    actions = ['print_pdfs']
    list_display = (
    'name', 'item_type', 'checked', 'published', 'has_image', 'has_pdf', 'last_update_date', 'expiration', 'tag_list')
    list_display_links = list_display
    ordering = ('name',)
    search_fields = ('name', 'published', 'checked', 'tags__name',)
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
                     'visual_description',
                     'published',
                     'checked',
                     'achievement_mechanics',
                     'print_duplication',
                     'tags',
                 )
         }),
        ('Crafting and Usage', {
            'classes': ('collapse',),
            'fields': ('crafting_tree', 'crafting_area', 'usage_tree'),
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('details', 'season'),
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

    def tag_list(self, obj):
        the_tags = obj.tags.all().order_by('name')
        return u", ".join(o.name for o in the_tags)

    def get_changeform_initial_data(self, request):
        get_data = super(ModuleAssemblyAdmin, self).get_changeform_initial_data(request)
        get_data['registrar'] = request.user.pk
        return get_data

    def get_form(self, request, obj=None, **kwargs):
        form = super(ModuleAssemblyAdmin, self).get_form(request, obj, **kwargs)

        if 'name' in form.base_fields:
            form.base_fields['name'].widget.attrs['style'] = 'width: 45em;'

        if 'achievement_mechanics' in form.base_fields:
            form.base_fields['achievement_mechanics'].widget.attrs['style'] = 'width: 45em;'

        if 'print_duplication' in form.base_fields:
            form.base_fields['print_duplication'].widget.attrs['style'] = 'width: 45em;'

        if 'tags' in form.base_fields:
            form.base_fields['tags'].widget.attrs['style'] = 'width: 100em; height: 5em;'

        if 'details' in form.base_fields:
            form.base_fields['details'].widget.attrs['style'] = 'width: 100em; height: 5em;'

        return form


@admin.register(FinancialInstitution)
class FinancialInstitutionAdmin(NestedModelAdmin):
    list_display = ('branch', 'name', 'active', 'published', 'modifier', 'registry_date', 'registrar')
    list_display_links = list_display
    ordering = ('branch', 'name',)
    search_fields = ('branch', 'name',)

    inlines = [
        FinancialInstitutionPictureInLine
    ]

    fieldsets = (
        (None,
         {
             'fields':
                 (
                     'branch',
                     'name',
                     'slug',
                     'text',
                     'active',
                     'published',
                     'modifier',
                 )
         }),
        ('Registrar', {
            'classes': ('collapse',),
            'fields': ('registrar', 'registry_date',),
        }),
    )

    def get_changeform_initial_data(self, request):
        get_data = super(FinancialInstitutionAdmin, self).get_changeform_initial_data(request)
        get_data['registrar'] = request.user.pk
        return get_data


@admin.register(FinancialInvestment)
class FinancialInvestmentAdmin(admin.ModelAdmin):
    list_display = (
    'character', 'investment_date', 'institution', 'amount_invested', 'die_roll', 'modifier', 'roll_total',
    'end_result',)
    list_display_links = list_display
    ordering = ('-investment_date', 'institution', 'character', 'amount_invested')
    # search_fields = ('institution', 'character',)
    add_form = FinancialInvestmentAddForm
    change_form_template = "necrotopia/investment_admin.html"
    add_form_template = "necrotopia/investment_admin.html"
    readonly_fields = ('die_roll', 'modifier', 'end_result')
    show_close_button = True

    fieldsets = (
        (None,
         {
             'fields': ('character', 'institution', 'investment_date',)
         }),
        ('Results', {
            'classes': ('expand',),
            'fields': ('amount_invested', 'die_roll', 'modifier', 'end_result'),
        }),
    )

    def institution_modifier(self, request):
        if type(request) is FinancialInvestment:
            institution = request.institution
            return str(FinancialInstitutionModifier(institution.modifier))

    def end_result(self, request):
        if type(request) is FinancialInvestment:
            investment_result = InvestmentResult.descriptor_from_die_result(request.roll_total)

            return investment_result

    def each_context(self, request):
        context = super().each_context(request)
        context['show_close'] = True
        return context

    @staticmethod
    def die_roll_and_save(self, request, obj):
        if "_roll_investment;" in request.POST:
            die_string = ''
            institution = obj.institution
            if institution.modifier > 0:
                die_string += "1d6+{modifier}".format(modifier=institution.modifier)
            elif institution.modifier < 0:
                die_string += "1d6{modifier}".format(modifier=institution.modifier)
            else:
                die_string += "1d6"

            result, explanation = rolldice.roll_dice('1d6')
            roll_total = result + institution.modifier
            result_string = InvestmentResult.instructions_from_die_result(roll_total)

            obj.die_roll = result
            obj.modifier = institution.modifier
            obj.roll_total = roll_total
            obj.save()
            self.message_user(request,
                              "Rolled: {die_string}={roll_total} [{result_string}]".format(die_string=die_string,
                                                                                           roll_total=roll_total,
                                                                                           result_string=result_string))
        return super().response_change(request, obj)

    def response_change(self, request, obj):
        return FinancialInvestmentAdmin.die_roll_and_save(self, request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        return FinancialInvestmentAdmin.die_roll_and_save(self, request, obj)


@admin.register(Advertisement)
class AdvertisementCarouselAdmin(admin.ModelAdmin):
    list_display = ('name', 'published')
    list_display_links = ('name',)

    class Meta:
        model = Advertisement

    def get_changeform_initial_data(self, request):
        get_data = super(AdvertisementCarouselAdmin, self).get_changeform_initial_data(request)
        get_data['registrar'] = request.user.pk
        return get_data
