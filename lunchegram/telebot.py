import telebot
from django.conf import settings


bot = telebot.TeleBot(settings.SOCIAL_AUTH_TELEGRAM_BOT_TOKEN)
