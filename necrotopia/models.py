from datetime import timedelta
from enum import IntEnum

from django.contrib.auth.models import AbstractBaseUser, AbstractUser, Group, Permission, User, \
    PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _translate
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
from taggit.forms import TagField
from taggit.managers import TaggableManager
from taggit.models import Tag

from necrotopia.managers import CustomUserManager

USERNAME_FIELD = 'email'


class Months(IntEnum):
    January = 1
    February = 2
    March = 3
    April = 4
    May = 5
    June = 6
    July = 7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Grade(IntEnum):
    Ungraded = 0
    Basic = 1
    Proficient = 2
    Master = 3

    def __str__(self):
        return str(self.name)

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class TimeUnits(IntEnum):
    No_Expiration = 0
    end_of_event = 1
    hours = 2
    days = 3
    months = 4
    years = 5

    def __str__(self):
        return str(self.name)

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ComponentType(IntEnum):
    Scrap = 0
    Herb = 1
    Weapon = 2
    Gizmo = 3
    Produce = 4
    Brew = 5
    Meal = 6
    Injectable = 7
    Armor = 8
    Vehicle = 9
    Room_Augment = 10
    Weapon_Augment = 11
    Armor_Augment = 12
    Vehicle_Augment = 13
    Trap = 14
    Shield_Augment = 15
    Ranged_Exotic = 16
    Melee_Exotic = 17

    def __str__(self):
        return str(self.name)

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class SkillCategory(IntEnum):
    Combat = 1
    Civilized = 2
    Wasteland = 3
    Anomaly = 4
    Lore = 5

    def __str__(self):
        return str(self.name)

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Title(models.Model):
    descriptor = models.CharField(max_length=30, blank=False, null=False)

    def __str__(self):
        return self.descriptor

    @classmethod
    def choices(cls):
        return [(item.id, item.descriptor) for item in Title.objects.all()]


class Gender(models.Model):
    descriptor = models.CharField(max_length=30, blank=False, null=False)

    def __str__(self):
        return self.descriptor

    @classmethod
    def choices(cls):
        return [(item.id, item.descriptor) for item in Gender.objects.all()]


class UserProfile(AbstractBaseUser, PermissionsMixin):
    display_name = models.CharField(max_length=255, null=False, blank=False)
    full_name = models.CharField(max_length=255, null=False, blank=False)
    email_validator = EmailValidator()
    email = models.EmailField(_translate('email address'), max_length=254, unique=True, blank=False,
                              validators=[email_validator],
                              error_messages={"unique": _translate('A user with that username already exists')})
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='django_user_title', null=True, blank=True)
    pronouns = models.CharField(max_length=255, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, null=True, blank=True)
    display_game_advertisements = models.BooleanField(default=True, null=True, blank=True)

    is_staff = models.BooleanField(
        _translate("staff status"),
        default=False,
        help_text=_translate("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _translate("active"),
        default=True,
        help_text=_translate(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    is_superuser = models.BooleanField(
        _translate("superuser status"),
        default=False,
        help_text=_translate(
            "Designates whether this user should be treated as a superuser. "
        ),
    )

    date_joined = models.DateTimeField(_translate("date joined"), default=timezone.now)
    birth_date = models.DateTimeField(_translate("birth_date"), blank=True, null=True)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    # REQUIRED_FIELDS = ["email"]

    def __str__(self):
        output_string = self.email
        if len(self.display_name) > 0:
            output_string = "{name} {display_name}".format(name=self.email, display_name=self.display_name)

        return self.email

    class Meta:
        verbose_name = _translate('user')
        verbose_name_plural = _translate('users')
        abstract = False

    def save(self, *args, **kwargs):
        if self.email is not None:
            super(UserProfile, self).save(*args, **kwargs)
        else:
            pass

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class UsefulLinks(models.Model):
    name = models.CharField(max_length=255, unique=False, blank=False, null=False)
    description = models.CharField(max_length=500, unique=False, blank=True, null=True)
    url = models.URLField(blank=False, null=False)
    published = models.BooleanField(blank=False, null=False, default=True)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    chapter_link = models.ForeignKey('Chapter', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "{name} {url}".format(name=self.name, url=self.url)

    def clean(self):
        cleaned_data = super(UsefulLinks, self).clean()
        if self.chapter_link.pk is None:
            if self.chapter_link.registrar is not None:
                self.registrar = self.chapter_link.registrar
                self.registrar_id = self.chapter_link.registrar_id

        return cleaned_data

    class Meta:
        verbose_name_plural = "Chapter Useful Links"
        verbose_name = "Chapter Useful Link"


class ChapterStaffType(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    registry_date = models.DateTimeField('registry_date', default=timezone.now, blank=False, null=False)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "chapter staff type"


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    registry_date = models.DateTimeField('registry_date', default=timezone.now, blank=False, null=False)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return self.name


class ChapterStaff(models.Model):
    user_profile = models.ForeignKey(UserProfile, blank=False, null=False, on_delete=models.CASCADE)
    type = models.ForeignKey(ChapterStaffType, blank=False, null=False, on_delete=models.CASCADE)
    chapter_link = models.ForeignKey('Chapter', blank=True, null=True, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, blank=True, null=True, on_delete=models.CASCADE)

    def email(self):
        return self.user_profile.email

    def display_name(self):
        return self.user_profile.display_name

    def __str__(self):
        return self.user_profile.display_name


class ChapterPicture(models.Model):
    picture = models.ImageField(upload_to='chapter_images')
    chapter_item = models.ForeignKey('Chapter', blank=False, null=False, on_delete=models.CASCADE, related_name='picture_chapter')

    def image_preview(self):
        if self.picture:
            return mark_safe(
                '<a href="%s"><img src="%s" width="150" height="150" /></a>' % (self.picture.url, self.picture.url))
        else:
            return '(No image)'

    def __str__(self):
        return self.picture.name


class Chapter(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    active = models.BooleanField(blank=False, null=False, default=True)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='chapter_registrar')
    useful_links = models.ForeignKey(UsefulLinks, on_delete=models.CASCADE, blank=True, null=True)
    staff = models.ForeignKey(ChapterStaff, null=True, blank=True, on_delete=models.CASCADE)
    chapter_pictures = models.ForeignKey(ChapterPicture, blank=True, null=True, on_delete=models.CASCADE, related_name='pictures')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "chapters"

    def get_changeform_initial_data(self, request):
        get_data = super(self).get_changeform_initial_data(request)
        get_data['registrar'] = request.user.pk
        return get_data


class ResourceItem(models.Model):
    name = models.CharField(max_length=255, unique=False)
    expiration_units = models.SmallIntegerField(default=6, blank=True, null=True)
    time_units = models.IntegerField(choices=TimeUnits.choices(), default=TimeUnits.months)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    tags = TaggableManager(blank=True, verbose_name='Tags', help_text='A comma-separated list of tags')
    rated_skills = models.ForeignKey('RatedSkillItem', on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='related_skills')

    def get_expiration(self):
        if self.expiration_units == 0 or self.time_units == TimeUnits.No_Expiration:
            return 'None'
        else:
            expiration_units_string = str(self.expiration_units)
            time_string = TimeUnits(self.time_units).name

            return f'{expiration_units_string} {time_string}'

    def get_tags_string(self):
        return ', '.join(t for t in self.tags.names())

    def get_related_skills(self):
        return ''
        # filtered = RatedSkillItem.objects.filter(self.rated_skills)
        # print(dir(filtered))
        # if self > 0:
        #     foo = self.rated_skills.objects
        #     print(dir(foo))
        #     return ", ".join(str(skill.name) for skill in foo)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'


class SkillItem(models.Model):
    name = models.CharField(max_length=255, unique=False)
    category = models.IntegerField(choices=sorted(SkillCategory.choices(), key=lambda x: x[1]), default=SkillCategory.Anomaly)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    tags = TaggableManager(blank=True, verbose_name='Tags', help_text='A comma-separated list of tags')
    skill_ratings = models.ForeignKey('SkillRatings', on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='skill_ratings')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def get_tags_string(self):
        return ', '.join(t for t in self.tags.names())

    def get_item_type(self):
        return SkillCategory(self.category).name

    def trunc_description(self):
        result = ''
        if self.skillratings_set is not None:
            first = self.skillratings_set.first()
            if first is not None:
                result = "{description}...".format(description=first.description[:50])

        return result


class SkillRatings(models.Model):
    grade = models.IntegerField(choices=Grade.choices(), default=Grade.Basic)
    skill = models.ForeignKey(SkillItem, on_delete=models.CASCADE, blank=False, null=False)
    description = models.CharField(max_length=3000, unique=False)

    class Meta:
        ordering = ['grade', ]
        verbose_name = 'SkillRating'
        verbose_name_plural = 'SkillRatings'

    def get_item_type(self):
        return Grade(self.grade).name


class RatedSkillItem(models.Model):
    resource_item = models.ForeignKey('ResourceItem', on_delete=models.CASCADE)
    grade = models.IntegerField(choices=Grade.choices(), default=Grade.Basic)
    skill = models.ForeignKey(SkillItem, on_delete=models.CASCADE, blank=False, null=False)
    mind = models.IntegerField(default=5, blank=True, null=True)
    time = models.IntegerField(default=10, blank=True, null=True)
    one_use_per_game = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        x = Grade(self.grade).name
        return f'{x} {self.skill.name} [{self.mind} mind , {self.time} minutes]'


class RulePicture(models.Model):
    picture = models.ImageField(upload_to='static_images')
    rule_item = models.ForeignKey('Rule', blank=False, null=False, on_delete=models.CASCADE,
                                  related_name='picture_rule')

    def image_preview(self):
        if self.picture:
            return mark_safe(
                '<a href="%s"><img src="%s" width="150" height="150" /></a>' % (self.picture.url, self.picture.url))
        else:
            return '(No image)'

    def __str__(self):
        return self.picture.name


class Rule(models.Model):
    name = models.CharField(max_length=255, unique=False)
    reference = models.CharField(max_length=255, unique=False, blank=True, null=True)
    slug = models.CharField(max_length=255, unique=False, blank=True, null=True)
    text = models.CharField(max_length=2048, unique=False, blank=True, null=True)
    creation_date = models.DateTimeField('creation_date', default=timezone.now)
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    tags = TaggableManager(blank=True, verbose_name='Tags', help_text='A comma-separated list of tags')
    pictures = models.ForeignKey(RulePicture, blank=True, null=True, on_delete=models.CASCADE, related_name='pictures')

    def __str__(self):
        return self.name

    def get_tags_string(self):
        return ', '.join(t for t in self.tags.names())

    def partial_slug(self):
        return "{slug}...".format(slug=self.slug[:50])


class ItemPdf(models.Model):
    pdf = models.FileField(upload_to='pdf/', null=True, blank=True)
    pdf_assembly_item = models.ForeignKey('ModuleAssembly', blank=False, null=False, on_delete=models.CASCADE,
                                      related_name='pdf_picture_ModuleAssembly')


class ItemPicture(models.Model):
    picture = models.ImageField(upload_to='static_images')
    imd_assembly_item = models.ForeignKey('ModuleAssembly', blank=False, null=False, on_delete=models.CASCADE,
                                      related_name='img_picture_ModuleAssembly')

    def image_preview(self):
        if self.picture:
            return mark_safe(
                '<a href="%s"><img src="%s" width="150" height="150" /></a>' % (self.picture.url, self.picture.url))
        else:
            return '(No image)'

    def __str__(self):
        return self.picture.name


class ModuleGradeResource(models.Model):
    quantity = models.IntegerField(default=1)
    resource = models.ForeignKey(ResourceItem, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name='%(class)s_resource')
    parent_grade = models.ForeignKey('ModuleGrade', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'

    def __str__(self):
        return ''


class ModuleGradeSubAssembly(models.Model):
    quantity = models.IntegerField(default=1)
    grade = models.IntegerField(choices=Grade.choices(), default=Grade.Ungraded)
    assembly = models.ForeignKey('ModuleAssembly', on_delete=models.CASCADE, blank=True, null=True,
                                 related_name='%(class)s_sub_assembly')
    parent_grade = models.ForeignKey('ModuleGrade', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name = 'Crafted Item'
        verbose_name_plural = 'Crafted Items'

    def __str__(self):
        return ''


class ModuleGrade(models.Model):
    grade = models.IntegerField(choices=Grade.choices(), default=Grade.Basic)
    name = models.CharField(max_length=255, unique=False)
    mind = models.IntegerField(default=5, blank=True, null=True)
    time = models.IntegerField(default=20, blank=True, null=True)
    mechanics = models.CharField(max_length=1000, blank=True, null=True)
    module_assembly = models.ForeignKey('ModuleAssembly', on_delete=models.CASCADE, blank=True, null=True,
                                        related_name='moduleAssembly_parent')
    resources = models.ForeignKey(ModuleGradeResource, on_delete=models.CASCADE, blank=True, null=True)
    sub_assemblies = models.ForeignKey(ModuleGradeSubAssembly, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_grade_name(self):
        return Grade(self.grade).name

    def get_grade_resources(self):
        return self.resources

    class Meta:
        verbose_name = 'Item Grade'
        verbose_name_plural = 'Item Grades'


class ModuleAssembly(models.Model):
    line_id = models.AutoField(primary_key=True, blank=False, null=False, unique=True)
    name = models.CharField(max_length=255, unique=False)
    expiration_units = models.SmallIntegerField(default=0, blank=True, null=True)
    time_units = models.IntegerField(choices=TimeUnits.choices(), default=TimeUnits.No_Expiration)
    item_type = models.IntegerField(choices=ComponentType.choices(), default=ComponentType.Gizmo)
    achievement_mechanics = models.CharField(blank=True, null=True, max_length=1000)
    print_duplication = models.CharField(blank=True, null=True, max_length=1000)
    details = models.CharField(blank=True, null=True, max_length=1000)
    registration_date = models.DateTimeField('registration_date', default=timezone.now)
    last_update_date = models.DateTimeField('last_update_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    crafting_tree = models.CharField(max_length=100, unique=False, blank=True, null=True, default='Artisan')
    crafting_area = models.CharField(max_length=100, unique=False, blank=True, null=True,
                                     default='Mechanical Crafting Zone')
    usage_tree = models.CharField(max_length=100, unique=False, blank=True, null=True, default='n/a')
    update_required = models.BooleanField(default=False, blank=True, null=True)
    visual_description = models.CharField(max_length=1000, unique=False, blank=True, null=True)
    season = models.CharField(max_length=50, unique=False, blank=True, null=True)
    published = models.BooleanField(default=True)
    checked = models.BooleanField(default=False)
    tags = TaggableManager(blank=True, verbose_name='Tags', help_text='A comma-separated list of tags')
    module_grades = models.ForeignKey(ModuleGrade, on_delete=models.CASCADE, blank=True, null=True,
                                      related_name='moduleGrade_grades')

    def flatten(self):
        result = dict()
        grades = ModuleGrade.objects.filter(module_assembly_id=self.line_id)

        if grades is not None:
            for grade in grades:
                pass

        return result

    def get_item_type(self):
        return ComponentType(self.item_type).name

    def get_tags_string(self):
        return ', '.join(t for t in self.tags.names())

    def get_expiration(self):
        if self.expiration_units == 0 or self.time_units == TimeUnits.No_Expiration:
            return 'None'
        else:
            expiration_units_string = str(self.expiration_units)
            time_string = TimeUnits(self.time_units).name

            return f'{expiration_units_string} {time_string}'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Blueprint'
        verbose_name_plural = 'Blueprints'


class Character(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=False, blank=False, null=False)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='registrar')

    def __str__(self):
        return self.name


class FinancialInstitutionModifier(IntEnum):
    very_poor = -3
    poor = -2
    below_average = -1
    average = 0
    good = 1
    very_good = 2
    outstanding = 3

    def __str__(self):
        return "{label} ({modifier})".format(label=self.name, modifier=self.value).title().replace("_", " ")

    @classmethod
    def choices(cls):
        return [(key.value, str(key)) for key in cls]


class InstitutionPicture(models.Model):
    picture = models.ImageField(upload_to='institutions_images')
    institution_item = models.ForeignKey('FinancialInstitution', blank=False, null=False, on_delete=models.CASCADE, related_name='picture_institution')

    def image_preview(self):
        if self.picture:
            return mark_safe(
                '<a href="%s"><img src="%s" width="150" height="150" /></a>' % (self.picture.url, self.picture.url))
        else:
            return '(No image)'

    def __str__(self):
        return self.picture.name


class FinancialInstitution(models.Model):
    branch = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    slug = models.CharField(max_length=255, unique=False, blank=True, null=True)
    text = models.CharField(max_length=2048, unique=False, blank=True, null=True)
    active = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    modifier = models.IntegerField(choices=FinancialInstitutionModifier.choices(),
                                   default=FinancialInstitutionModifier.average, blank=False, null=False)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    institution_pictures = models.ForeignKey(InstitutionPicture, blank=True, null=True, on_delete=models.CASCADE, related_name='pictures')

    def __str__(self):
        return "{} [{:+}]".format(self.name, self.modifier)


class FinancialInvestment(models.Model):
    character = models.ForeignKey(Character, blank=False, null=False, on_delete=models.CASCADE, related_name='character')
    institution = models.ForeignKey(FinancialInstitution, blank=False, null=False, on_delete=models.CASCADE)
    amount_invested = models.IntegerField(blank=False, null=False, default=4)
    die_roll = models.IntegerField(blank=False, null=False, default=1)
    modifier = models.IntegerField(blank=False, null=False, default=0)
    roll_total = models.IntegerField(blank=False, null=False, default=0)
    investment_date = models.DateTimeField('investment_date', default=timezone.now)

    def __str__(self):
        return "{character} invested {currency} currency in {institution} on {date}".format(character=self.character, currency=self.amount_invested, institution=self.institution.name, date=self.investment_date)


class LootTableItem(models.Model):
    item_name = models.CharField(max_length=255, unique=True)
    probability = models.FloatField(null=False, blank=False,
                                    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    loot_table = models.ForeignKey('LootTable', blank=False, null=False, on_delete=models.CASCADE,
                                   related_name='loot_table')

    class Meta:
        constraints = (
            # for checking in the DB
            CheckConstraint(
                check=Q(probability__gte=0.0) & Q(probability__lte=1.0),
                name='probability_range'),
        )

    def __str__(self):
        return self.item_name


class LootTable(models.Model):
    name = models.CharField(max_length=255, unique=True)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    loot_items = models.ForeignKey(LootTableItem, blank=True, null=True, on_delete=models.CASCADE,
                                   related_name='loot_items')

    def __str__(self):
        return self.name


class InvestmentResult(IntEnum):
    Major_Loss = 1
    Minor_Loss = 2
    Break_Even = 3
    Minor_Gain = 4
    Major_Gain = 5
    Jackpot = 6

    def __str__(self):
        return str(self.name)

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @staticmethod
    def instructions_from_die_result(die_result: int):
        result = "Major Loss - collect 4 from player"
        match die_result:
            case InvestmentResult.Minor_Loss:
                result = "Minor Loss - collect 2 from player"
            case InvestmentResult.Break_Even:
                result = "Broke Even - give player back 4"
            case InvestmentResult.Minor_Gain:
                result = "Minor Gain - give player back 5"
            case InvestmentResult.Major_Gain:
                result = "Major gain - give player back 6"
            case _ if die_result >= InvestmentResult.Jackpot:
                result = "Jackpot! - give player back 8"
            case other:
                result = result

        return result
    @staticmethod
    def descriptor_from_die_result(die_result: int):
        result = "Major Loss - lost investment"
        match die_result:
            case InvestmentResult.Minor_Loss:
                result = "Minor Loss - lost half of investment"
            case InvestmentResult.Break_Even:
                result = "Broke Even - no gain, no losses"
            case InvestmentResult.Minor_Gain:
                result = "Minor Gain - gained 1"
            case InvestmentResult.Major_Gain:
                result = "Major gain - gained 2"
            case _ if die_result >= InvestmentResult.Jackpot:
                result = "Jackpot! - gained 4"
            case other:
                result = result

        return result


class Advertisement(models.Model):
    name = models.CharField(max_length=60, default='', blank=True)
    slug = models.TextField(max_length=100, default='', blank=True)
    link = models.URLField(max_length=1000, default='', blank=True, null=True)
    image = models.ImageField(upload_to='advertisements')
    published = models.BooleanField(default=False)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now() + timedelta(days=30))
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'
