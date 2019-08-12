import uuid
from secrets import token_urlsafe

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from djchoices import DjangoChoices, ChoiceItem
from model_utils.managers import SoftDeletableManagerMixin, SoftDeletableQuerySetMixin
from model_utils.models import TimeStampedModel, SoftDeletableModel


def sane_repr(*attrs):
    if 'id' not in attrs and 'pk' not in attrs:
        attrs = ('id', ) + attrs

    def _repr(self):
        cls = type(self).__name__

        pairs = ('%s=%s' % (a, repr(getattr(self, a, None))) for a in attrs)

        return u'<%s at 0x%x: %s>' % (cls, id(self), ', '.join(pairs))

    return _repr


class CompanyQuerySet(SoftDeletableQuerySetMixin, models.QuerySet):
    def privacy_link(self):
        return self.filter(privacy_mode=Company.Privacy.link)


class CompanyManager(SoftDeletableManagerMixin, models.Manager.from_queryset(CompanyQuerySet)):
    _queryset_class = CompanyQuerySet


class Company(TimeStampedModel, SoftDeletableModel):
    class Privacy(DjangoChoices):
        link = ChoiceItem()

    name = models.CharField(max_length=255)
    privacy_mode = models.CharField(max_length=10, choices=Privacy.choices)
    invite_token = models.CharField(max_length=50, blank=True, null=True, unique=True)
    employees = models.ManyToManyField(settings.AUTH_USER_MODEL, through='core.Employee', related_name='companies')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='owned_companies')

    objects = CompanyManager()

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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'has_telegram': True})
    state = models.CharField(max_length=10, choices=State.choices, default=State.online)

    class Meta:
        verbose_name = _('employee')
        verbose_name_plural = _('employees')
        unique_together = [
            ['company', 'user'],
        ]

    __repr__ = sane_repr('user', 'state')


class Lunch(TimeStampedModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='lunches')
    date = models.DateField()
    # confirmations_created_at = models.DateTimeField(blank=True, null=True)
    # auto_decline_after = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'lunch'
        verbose_name_plural = 'lunches'
        unique_together = [
            ['company', 'date'],
        ]


class LunchGroup(TimeStampedModel):
    lunch = models.ForeignKey(Lunch, on_delete=models.CASCADE, related_name='groups')
    employees = models.ManyToManyField(Employee, through='LunchGroupMember')

    class Meta:
        verbose_name = 'lunch group'
        verbose_name_plural = 'lunch groups'


class LunchGroupMember(TimeStampedModel):
    lunch_group = models.ForeignKey(LunchGroup, on_delete=models.CASCADE, related_name='members')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    notified_at = models.DateTimeField(blank=True, null=True)
    notification_message_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'lunch group member'
        verbose_name_plural = 'lunch group members'
        unique_together = [
            ['lunch_group', 'employee'],
        ]

    @property
    def is_notified(self):
        return self.notified_at is not None


class TelegramChat(TimeStampedModel):
    """Stores every chat with the bot (for possible future use)"""
    chat_id = models.CharField(max_length=255, unique=True)
    uid = models.CharField(max_length=255, unique=True)


# class LunchSchedule(TimeStampedModel, SoftDeletableModel):
#     class Weekday(DjangoChoices):
#         monday = ChoiceItem(value=0)
#         tuesday = ChoiceItem(value=1)
#         wednesday = ChoiceItem(value=2)
#         thursday = ChoiceItem(value=3)
#         friday = ChoiceItem(value=4)
#         saturday = ChoiceItem(value=5)
#         sunday = ChoiceItem(value=6)
#
#     company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='lunch_schedules')
#     weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
#     confirm_delta = models.PositiveSmallIntegerField(
#         default=2, validators=[MaxValueValidator(6)],
#         help_text='We will send confirmation request specified number of days before lunch. '
#                   'We send all messages around 10:00 AM.')
#     confirm_timeout = models.PositiveSmallIntegerField(
#         default=24, validators=[MaxValueValidator(6*24)],
#         help_text='User will have specified amount of hours to confirm request. '
#                   'After that time request will be declined automatically.\n'
#                   'At least one day should remain before lunch.')
#
#     class Meta:
#         verbose_name = 'lunch schedule'
#         verbose_name_plural = 'lunch schedules'
#         unique_together = [
#             ['company', 'weekday'],
#         ]
#
#     def __str__(self):
#         return self.get_weekday_display()
#
#
# class ConfirmationRequest(TimeStampedModel):
#     class Status(DjangoChoices):
#         new = ChoiceItem()
#         delivered = ChoiceItem()
#         confirmed = ChoiceItem()
#         declined = ChoiceItem()
#         auto_declined = ChoiceItem()
#
#     lunch = models.ForeignKey(Lunch, on_delete=models.CASCADE, related_name='confirmation_requests')
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='confirmation_requests')
#     status = models.CharField(max_length=20, choices=Status.choices, default=Status.new)
#
#     class Meta:
#         verbose_name = 'confirmation request'
#         verbose_name_plural = 'confirmation requests'
