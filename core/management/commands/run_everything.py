from django.core.management.base import BaseCommand
from core.tasks import run_everything


class Command(BaseCommand):
    help = 'Run lunch generation right now'

    def handle(self, *args, **options):
        run_everything.delay()
