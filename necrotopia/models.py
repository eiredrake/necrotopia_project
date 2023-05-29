from django.contrib.auth.models import AbstractBaseUser, AbstractUser, Group, Permission, _user_get_permissions, User, \
    PermissionsMixin
from django.core.validators import EmailValidator
from django.db import models
from django.db.models.manager import EmptyManager
from django.utils import timezone
from django.utils.translation import gettext as _translate

from necrotopia.managers import CustomUserManager
from django.core.mail import send_mail


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email_validator = EmailValidator()
    email = models.EmailField(_translate('email address'), max_length=254, unique=True, blank=False,
                              help_text=_translate('Required. 254 characters or fewer. Letters, digits and @/./+/-/_ '
                                                   'only.'), validators=[email_validator],
                              error_messages={"unique": _translate('A user with that username already exists')})

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

# Create your models here.
# class Pronoun(models.Model):
#     text = models.CharField(max_length=50, unique=True, blank=False, null=False)
#
#     def __str__(self):
#         return self.text
#
#     @classmethod
#     def get_default_pk(cls):
#         event_category, created = cls.objects.get_or_create(text='Not Set')
#         return event_category.pk
#
#     class Meta:
#         verbose_name = "Pronoun"
#         verbose_name_plural = "Pronouns"
#
#
# class SystemUser(AbstractUser):
#     middle_name = models.CharField(max_length=150, blank=True, null=True)
# preferred_pronouns = models.ForeignKey(to=Pronoun, on_delete=models.CASCADE, default=Pronoun.get_default_pk, blank=True, null=True)
# home_branch = models.ForeignKey(to='Branch', on_delete=models.CASCADE, blank=True, null=True)


# class BranchStaffType(models.Model):
#     name = models.CharField(max_length=255, unique=True, blank=False, null=False)
#     description = models.CharField(max_length=255, blank=True, null=True)
#     registry_date = models.DateTimeField('registry_date', default=timezone.now)
#     registrar = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name_plural = "branches staff type"
#
#
# class Branch(models.Model):
#     name = models.CharField(max_length=255, unique=True, blank=False, null=False)
#     registry_date = models.DateTimeField('registry_date', default=timezone.now)
#     registrar = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name_plural = "branches"
