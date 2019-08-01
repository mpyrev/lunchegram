import factory

from accounts.models import User


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'john{n}')
    has_telegram = True

    class Meta:
        model = User
