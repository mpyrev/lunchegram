from typing import Optional

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.functional import cached_property
from social_django.models import UserSocialAuth

from lunchegram import bot


class CustomUserManager(UserManager):
    def get_from_telegram_uid(self, uid: int) -> Optional['User']:
        social_user = UserSocialAuth.objects.get_social_auth('telegram', uid)
        if social_user:
            return social_user.user
        return None


class User(AbstractUser):
    has_telegram = models.BooleanField(default=False)
    telegram_chat_id = models.CharField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()

    @cached_property
    def telegram_account(self):
        try:
            account = self.social_auth.filter(provider='telegram').first()
        except UserSocialAuth.DoesNotExist:
            account = None
        return account

    def send_message(self, text):
        bot.send_message(self.telegram_chat_id, text)
