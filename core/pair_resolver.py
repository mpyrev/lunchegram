from abc import ABCMeta
from itertools import combinations
from math import exp
from random import random
from typing import Tuple, Set, Dict, List

import attr
import networkx as nx
from django.db.models import QuerySet
from networkx import max_weight_matching

from core.models import Employee, LunchGroupMember, Company, LunchGroup


@attr.s(slots=True)
class LunchMapEmployee:
    employee = attr.ib(type=Employee)


class DefaultEstimator:
    def __init__(self, lunch_map: Dict[]):
        self.lunch_map = None

    def get_weight(self, employee1: Employee, employee2: Employee) -> float:
        """
        Returns weight of edge between two employees.

        Here we should take into account preferences of both employees and combine them into unified weight.
        """
        weight = random()

        members = LunchGroupMember.objects.filter(employee=employee1, lunchgroup__employees=employee2).select_related('lunch').order_by('-lunch__date')
        if members.exists():
            # Apply decay so employees from lunches further away have better chances to meet again if
            # there are no fresh employees
            weight += exp(-8*x*x)
        else:
            # Never had lunch together bonus
            weight += 2

        return weight


@attr.s
class MaximumWeightGraphResolver:
    estimator_class = attr.ib(default=DefaultEstimator)

    def make_lunch_map(self, company: Company):
        LunchGroup.objects.filter(company=company)

    def get_estimator(self):
        return self.estimator_class()

    def resolve(self, company: Company, employees: List[Employee]) -> Set[Tuple[Employee]]:
        graph = nx.Graph()
        estimator = self.get_estimator()

        # Fill the graph
        graph.add_nodes_from(employees)
        for employee1, employee2 in combinations(employees, 2):
            weight = estimator.get_weight(employee1, employee2)
            graph.add_weighted_edges_from([(employee1, employee2, weight)])

        # Run matching algorithm
        matching = max_weight_matching(graph)
        return matching
