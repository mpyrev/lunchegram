from .celery import app as celery_app
from .telebot import bot


__all__ = ('celery_app', 'bot')
