from django.utils.translation import gettext as _

from core.telegram.state_registry import state_registry, NoStateException
from lunchegram import bot


__all__ = ['echo_message']


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    try:
        state_registry.process_message(message)
    except NoStateException:
        bot.reply_to(message, _("Sorry, I don't know this command."))
