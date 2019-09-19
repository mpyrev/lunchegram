from functools import wraps

from django.db import transaction

from accounts.models import User
from core.models import TelegramChat


def infuse_user():
    """
    Adds user instance to args if possible.
    Also creates
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = args[0]

            uid = message.from_user.id
            user = User.objects.get_from_telegram_uid(uid)

            if hasattr(message, 'chat'):
                with transaction.atomic():
                    TelegramChat.objects.get_or_create(uid=uid, defaults=dict(chat_id=message.chat.id))

            args = (user,) + args
            return func(*args, **kwargs)

        return wrapper

    return decorator
