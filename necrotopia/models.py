from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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
