from telebot.types import Message

from accounts.models import User
from core.telegram.decorators import infuse_user
from lunchegram import bot


__all__ = ['send_welcome']


@bot.message_handler(commands=['help', 'start'])
@infuse_user()
def send_welcome(user: User, message: Message):
    # Save chat_id for future direct messages
    if user:
        user.telegram_chat_id = message.chat.id
        user.save()
    bot.send_message(
        message.chat.id,
        "Hi! I'm random lunch bot.")
