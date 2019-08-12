from core.models import TelegramChat


def mark_telegram_user(backend, user, response, *args, **kwargs):
    user.has_telegram = backend.name == 'telegram'


def fill_telegram_chat_id(backend, user, uid, response, *args, **kwargs):
    if backend.name == 'telegram':
        try:
            chat = TelegramChat.objects.get(uid=uid)
        except TelegramChat.DoesNotExist:
            pass
        else:
            user.telegram_chat_id = chat.chat_id
