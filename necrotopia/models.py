from enum import IntEnum

from django.contrib.auth.models import AbstractBaseUser, AbstractUser, Group, Permission, User, \
    PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _translate
from imagekit.models import ImageSpecField
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


class Chapter(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    active = models.BooleanField(blank=False, null=False, default=True)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='chapter_registrar')
    useful_links = models.ForeignKey(UsefulLinks, on_delete=models.CASCADE, blank=True, null=True)
    staff = models.ForeignKey(ChapterStaff, null=True, blank=True, on_delete=models.CASCADE)

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
    category = models.IntegerField(choices=SkillCategory.choices(), default=SkillCategory.Combat)
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


class SkillRatings(models.Model):
    grade = models.IntegerField(choices=Grade.choices(), default=Grade.Basic)
    skill = models.ForeignKey(SkillItem, on_delete=models.CASCADE, blank=False, null=False)
    description = models.CharField(max_length=1000, unique=False)

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