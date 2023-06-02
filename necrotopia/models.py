from django.contrib.auth.models import AbstractBaseUser, AbstractUser, Group, Permission, User, \
    PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _translate
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from necrotopia.managers import CustomUserManager

USERNAME_FIELD = 'email'


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
    pronouns = models.CharField(max_length=255, null=False, blank=True)
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
        return self.email

    class Meta:
        verbose_name = _translate('user')
        verbose_name_plural = _translate('users')
        abstract = False

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


class ChapterStaffType(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "branches staff type"


class Chapter(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "branches"
