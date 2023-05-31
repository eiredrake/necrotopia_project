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


class Pronoun(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=256)

    subject = models.CharField(max_length=10, help_text="He, she, it")
    object = models.CharField(max_length=10, help_text="Her, him, it")
    reflexive = models.CharField(max_length=10, help_text="Itself, himself, herself")
    possessive_pronoun = models.CharField(max_length=10, help_text="Hers, his, its")
    possessive_determiner = models.CharField(max_length=10, help_text="His, her, its")

    def she_he(self): return self.subject
    def he_she(self): return self.subject
    def em(self): return self.subject

    def him_her(self): return self.object
    def her_him(self): return self.object
    def ey(self): return self.object

    def himself_herself(self): return self.reflexive
    def herself_himself(self): return self.reflexive
    def emself(self): return self.reflexive

    def his_hers(self): return self.possessive_pronoun
    def hers_his(self): return self.possessive_pronoun
    def eir(self): return self.possessive_pronoun

    def his_her(self): return self.possessive_determiner
    def her_his(self): return self.possessive_determiner
    def eirs(self): return self.possessive_determiner

    def __unicode__(self):
        return self.name

    def __str__(self):
        return "{name}: {subject}, {object}, {reflexive}, {possessive_pronoun}, {possessive_determiner}".format(name=self.name, subject=self.subject, object=self.object, reflexive=self.reflexive, possessive_pronoun=self.possessive_pronoun, possessive_determiner=self.possessive_determiner)


class UserProfile(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255, null=False, blank=False)
    display_name = models.CharField(max_length=255, null=False, blank=False)
    email_validator = EmailValidator()
    email = models.EmailField(_translate('email address'), max_length=254, unique=True, blank=False,
                              validators=[email_validator],
                              error_messages={"unique": _translate('A user with that username already exists')})
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='django_user_title', null=True, blank=True)
    pronouns = models.ForeignKey(Pronoun, on_delete=models.CASCADE, related_name='django_user_pronouns', null=True, blank=True)


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
