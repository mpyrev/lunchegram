from urllib.parse import urljoin

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from lunchegram import bot


class Command(BaseCommand):
    help = 'Resets Telegram webhooks'

    def add_arguments(self, parser):
        parser.add_argument(
            '-u', '--url',
            action='store',
            dest='webhook_url',
            help='URL to set as webhook',
        )

    def handle(self, *args, **options):
        url = options.get('webhook_url')
        if url is None:
            url = urljoin(settings.WEBHOOK_BASE_URL, reverse('webhook'), allow_fragments=False)
        bot.remove_webhook()
        bot.set_webhook(url=url)
