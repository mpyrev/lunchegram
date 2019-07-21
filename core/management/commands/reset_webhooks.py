from urllib.parse import urljoin

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
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
        # for poll_id in options['poll_ids']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()
        #
        #     self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))