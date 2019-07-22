from lunchegram import bot


__all__ = ['echo_message']


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, "Sorry, I don't know this command.")
