def mark_telegram_user(backend, user, response, *args, **kwargs):
    user.has_telegram = backend.name == 'telegram'
