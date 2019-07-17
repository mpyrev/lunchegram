import logging
import os

from telegram.ext import Updater, CommandHandler


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def main():
    updater = Updater(token=os.environ.get('LUNCHEGRAM_BOT_TOKEN'), use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
