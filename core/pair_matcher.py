from itertools import combinations
from random import random, choice
from typing import Tuple, Set, List

import attr
import networkx as nx
from networkx import max_weight_matching

from core.models import Employee, LunchGroupMember, Company, LunchGroup


@attr.s(slots=True)
class LunchMapEmployee:
    employee = attr.ib(type=Employee)


class DefaultEstimator:
    def __init__(self, lunch_map=None):
        self.lunch_map = lunch_map

    def get_weight(self, employee1: Employee, employee2: Employee) -> float:
        """
        Returns weight of edge between two employees.

        Here we should take into account preferences of both employees and combine them into unified weight.
        """
        weight = random()

        members = LunchGroupMember.objects.filter(
            employee=employee1, lunch_group__employees=employee2).select_related('lunch').order_by('-lunch__date')
        if members.exists():
            # Apply decay so employees from lunches further away have better chances to meet again if
            # there are no fresh employees
            # TODO: make actual decaying weight
            # weight += exp(-8*x*x)
            pass
        else:
            # Never had lunch together bonus
            weight += 2

        return weight


@attr.s(cmp=False)
class Node:
    employee = attr.ib(type=Employee)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return hash(self) == hash(other)


@attr.s
class MaximumWeightGraphMatcher:
    estimator_class = attr.ib(default=DefaultEstimator)

    def make_lunch_map(self, company: Company):
        LunchGroup.objects.filter(company=company)

    def get_estimator(self):
        return self.estimator_class()

    def match(self, company: Company, employees: List[Employee]) -> Set[Tuple[Employee]]:
        """
        Blossom graph matching algorithm.
        If number of users is odd we have to add copy of one of users to make a group of three.
        """
        graph = nx.Graph()
        estimator = self.get_estimator()

        # Select lucky employee to be part of a group of 3 if needed
        employees = list(employees)
        if len(employees) % 2:
            lucky_employee = choice(employees)
            employees.append(lucky_employee)

        # Fill the graph
        nodes = [Node(e) for e in employees]
        graph.add_nodes_from(nodes)
        for node1, node2 in combinations(nodes, 2):
            if node1.employee == node2.employee:
                continue
            weight = estimator.get_weight(node1.employee, node2.employee)
            graph.add_weighted_edges_from([(node1, node2, weight)])

        # Run matching algorithm
        matching = max_weight_matching(graph)

        # Find group of three if any
        group_map = {}
        for n1, n2 in matching:
            e1, e2 = n1.employee, n2.employee
            if e2 in group_map:
                e1, e2 = e2, e1
            if e1 in group_map:
                group_map[e1].add(e2)
                group_map[e2] = group_map[e1]
            else:
                group_map[e1] = group_map[e2] = {e1, e2}

        groups = set()
        for group in group_map.values():
            groups.add(frozenset(group))

        return groups
