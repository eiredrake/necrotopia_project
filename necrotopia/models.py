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
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE, )
    chapter_link = models.ForeignKey('Chapter', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "{name} {url}".format(name=self.name, url=self.url)

    class Meta:
        verbose_name_plural = "Chapter Useful Links"
        verbose_name = "Chapter Useful Link"

    def get_changeform_initial_data(self, request):
        get_data = super(self).get_changeform_initial_data(request)
        get_data['registrar'] = request.user.pk
        return get_data


class ChapterStaffType(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    registry_date = models.DateTimeField('registry_date', default=timezone.now, blank=False, null=False)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "chapter staff type"


class Chapter(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    active = models.BooleanField(blank=False, null=False, default=True)
    registry_date = models.DateTimeField('registry_date', default=timezone.now)
    registrar = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='chapter_registrar')
    useful_links = models.ForeignKey(UsefulLinks, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "chapters"
