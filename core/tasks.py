from django.db.models import F
from django.utils import timezone

from lunchegram import celery_app


@celery_app.task
def send_confirmation_requests():
    pass
