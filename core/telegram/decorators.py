from functools import wraps

from accounts.models import User


def infuse_user():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            obj = args[0]
            uid = obj.from_user.id
            user = User.objects.get_from_telegram_uid(uid)
            args = (user,) + args
            return func(*args, **kwargs)

        return wrapper

    return decorator
