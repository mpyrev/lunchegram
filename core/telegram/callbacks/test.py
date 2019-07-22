from core.telegram.decorators import infuse_user
from lunchegram import bot


__all__ = ['test']


@bot.message_handler(commands=['test'])
@infuse_user()
def test(user, message):
    bot.send_message(
        message.chat.id,
        str(user))
