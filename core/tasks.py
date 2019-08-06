from django.db import transaction
from django.utils import timezone

from accounts.models import User
from core.models import Company, Employee, LunchGroup, Lunch, LunchGroupMember
from core.pair_matcher import MaximumWeightGraphMatcher
from lunchegram import celery_app, bot


@celery_app.task
def run_everything():
    create_lunch_groups.delay()


@celery_app.task
def create_lunch_groups():
    for company_id in Company.objects.values_list('pk', flat=True):
        create_lunch_groups_for_company.delay(company_id)


@celery_app.task
@transaction.atomic()
def create_lunch_groups_for_company(company_id):
    company = Company.objects.get(pk=company_id)
    lunch = Lunch.objects.create(company=company, date=timezone.localdate())
    employees = Employee.objects.filter(company=company, state=Employee.State.online)
    matcher = MaximumWeightGraphMatcher()
    groups = matcher.match(company, employees)
    for group in groups:
        lunch_group = LunchGroup.objects.create(lunch=lunch)
        for employee in group:
            member = LunchGroupMember.objects.create(lunch_group=lunch_group, employee=employee)
            notify_lunch_group_member.delay(member.pk)


@celery_app.task
def notify_lunch_group_member(pk):
    member = LunchGroupMember.objects.get(pk=pk)
    user = member.employee.user
    if user.telegram_account:
        message = f'[inline mention of a user](tg://user?id={user.telegram_account.uid})'
        send_telegram_message.delay(user.pk, message)


@celery_app.task
def send_telegram_message(user_id, message):
    user = User.objects.get(pk=user_id)
    bot.send_message(user.telegram_chat_id, message)
