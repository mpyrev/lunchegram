from django.conf import settings
from redis import Redis


def get_redis():
    return Redis.from_url(settings.REDIS_URL)
