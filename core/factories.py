import factory

from accounts.factories import UserFactory
from core.models import Company, Employee


class CompanyFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'company{n}')
    privacy_mode = Company.Privacy.link
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = Company


class EmployeeFactory(factory.DjangoModelFactory):
    company = factory.SubFactory(CompanyFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Employee
