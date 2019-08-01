from django.test import TestCase

from core.factories import CompanyFactory, EmployeeFactory
from core.pair_matcher import MaximumWeightGraphMatcher


class PairMatcherTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory.create()

    def test_simple(self):
        employees = EmployeeFactory.create_batch(41, company=self.company)
        matcher = MaximumWeightGraphMatcher()
        groups = matcher.match(self.company, employees)
        print('\n'.join(
            [','.join(
                e.user.username for e in group
            ) for group in groups]
        ))
