from django.db import transaction
from django.utils.translation import gettext as _
from social_core.backends.telegram import TelegramAuth
from social_core.pipeline.user import get_username, create_user
from social_django.models import UserSocialAuth, DjangoStorage
from social_django.strategy import DjangoStrategy

from core.models import Company, Employee
from core.telegram.state_registry import state_registry
from lunchegram import bot


__all__ = ['join']


@bot.message_handler(commands=['join'])
def join(message):
    bot.send_message(
        message.chat.id,
        _('Please enter invite token provided by your coworker:'))
    state_registry.set_state(message.from_user.id, 'join_answer')


@state_registry.register('join_answer')
def process_join_answer(message):
    invite_token = message.text
    try:
        company = Company.objects.get(invite_token=invite_token)
    except Company.DoesNotExist:
        bot.reply_to(message, _("Sorry, couldn't find lunch group with the given token. :("))
        state_registry.del_state(message.from_user.id)
        return

    # Authenticate user, create if need to
    from_user = message.from_user
    try:
        social_auth = UserSocialAuth.objects.get(provider='telegram', uid=from_user.id)
    except UserSocialAuth.DoesNotExist:
        storage = DjangoStorage()
        strategy = DjangoStrategy(storage)
        backend = TelegramAuth(strategy)

        username = get_username(strategy, from_user.__dict__, backend)['username']
        with transaction.atomic():
            user = create_user(strategy, from_user.__dict__, backend, username=username)['user']
            user.first_name = from_user.first_name or ''
            user.last_name = from_user.last_name or ''
            user.has_telegram = True
            user.telegram_chat_id = message.chat.id
            user.save()
            UserSocialAuth.objects.get_or_create(provider='telegram', uid=from_user.id, defaults={
                'extra_data': from_user.__dict__,
                'user': user,
            })
    else:
        user = social_auth.user

    if not user.is_active:
        bot.send_message(message.chat.id, _('Sorry, your account has been deactivated.'))
        return

    # Create employee and add him to the group
    employee, created = Employee.objects.get_or_create(company=company, user=user)
    if created:
        msg = _("You've successfully joined lunch group «{}». "
                "You may manage your participation with /offline and /online commands.").format(company.name)
    else:
        msg = _("You've joined lunch group «{}» already. "
                "You may manage your participation with /offline and /online commands.").format(company.name)
    bot.send_message(message.chat.id, msg)
