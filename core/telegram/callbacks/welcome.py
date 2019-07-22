from lunchegram import bot


__all__ = ['send_welcome']


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Hi! I'm random lunch bot.")
