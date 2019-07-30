from abc import ABCMeta
from itertools import combinations
from random import random
from typing import Tuple

import attr
import networkx as nx
from django.db.models import QuerySet
from networkx import max_weight_matching

from accounts.models import User


#### Interfaces


class IPairResolver(metaclass=ABCMeta):
    def resolve(self, users: QuerySet) -> Tuple[Tuple[User]]:
        raise NotImplementedError


class IEstimator(metaclass=ABCMeta):
    def get_weight(self, user1: User, user2: User) -> float:
        raise NotImplementedError


#### Maximum weight matching graph algorithm (Blossom algorithm)


class DefaultEstimator(IEstimator):
    def get_weight(self, user1: User, user2: User) -> float:
        """
        Returns weight of edge between two users.

        Here we should take into account preferences of both users and combine them into unified weight.
        """
        return 1.0 + random()


@attr.s(slots=True)
class Edge:
    weight = attr.ib(type=float)


@attr.s
class MaximumWeightGraphResolver(IPairResolver):
    estimator_class = attr.ib(type=IEstimator, default=DefaultEstimator)

    def get_estimator(self) -> IEstimator:
        return self.estimator_class()

    def resolve(self, users: QuerySet) -> Tuple[Tuple[User]]:
        graph = nx.Graph()
        estimator = self.get_estimator()

        # Fill the graph
        graph.add_nodes_from(users)
        for user1, user2 in combinations(users, 2):
            weight = estimator.get_weight(user1, user2)
            graph.add_weighted_edges_from([(user1, user2, weight)])

        # Run matching algorithm
        matching = max_weight_matching(graph)
        return matching
