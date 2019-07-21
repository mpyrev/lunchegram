import uuid
from secrets import token_urlsafe

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from djchoices import DjangoChoices, ChoiceItem
from model_utils.models import TimeStampedModel


class CompanyQuerySet(models.QuerySet):
    def privacy_link(self):
        return self.filter(privacy_mode=Company.Privacy.link)


class Company(TimeStampedModel):
    class Privacy(DjangoChoices):
        link = ChoiceItem()

    name = models.CharField(max_length=255)
    privacy_mode = models.CharField(max_length=10, choices=Privacy.choices)
    invite_token = models.CharField(max_length=50, blank=True, null=True, unique=True)
    employees = models.ManyToManyField(settings.AUTH_USER_MODEL, through='core.Employee', related_name='companies')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='owned_companies')

    objects = CompanyQuerySet.as_manager()

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')

    def __str__(self):
        return self.name

    @staticmethod
    def generate_invite_token():
        return token_urlsafe(nbytes=32)


class Employee(TimeStampedModel):
    class State(DjangoChoices):
        online = ChoiceItem()
        offline = ChoiceItem()

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    state = models.CharField(max_length=10, choices=State.choices, default=State.online)

    class Meta:
        verbose_name = _('employee')
        verbose_name_plural = _('employees')
        unique_together = [
            ['company', 'user'],
        ]


class Schedule(TimeStampedModel):
    class Day(DjangoChoices):
        monday = ChoiceItem()
        tuesday = ChoiceItem()
        wednesday = ChoiceItem()
        thursday = ChoiceItem()
        friday = ChoiceItem()
        saturday = ChoiceItem()
        sunday = ChoiceItem()

    company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=15, choices=Day.choices)

    class Meta:
        verbose_name = 'schedule'
        verbose_name_plural = 'schedules'
        unique_together = [
            ['company', 'day_of_week'],
        ]

    def __str__(self):
        return self.get_day_of_week_display()
