from dataclasses import dataclass
from math import inf
from queue import PriorityQueue
from typing import Callable, Iterable, Tuple, Optional

from robotlib.nav import Nav, PathNode, NavPath
from robotlib.nav.heuristics import euclidean_heuristic
from robotlib.utils import DictWithDefault, or_default, PrioritizedItem, RunLimit


class AStar(Nav):
    """
    A* path planning.

    Implementation based on: https://en.wikipedia.org/wiki/A*_search_algorithm#Pseudocode
    """

    def __init__(
            self,
            neighbor_func: Callable[[PathNode], Iterable[Tuple[PathNode, float]]],
            heuristic: Callable[[PathNode, PathNode], float] = euclidean_heuristic,
            max_steps: int = None,
            max_cost: float = None,
    ):
        """
        :param neighbor_func: For a given node, it should return an iterable of tuples (neighbor, cost).
        :param heuristic: A function that estimates the cost to go from one node to another. Euclidian distance
            (the default) is good for most worlds, as the shortest distance between two points is a straight line.
        :param max_steps: Maximum number of nodes to evaluate before stopping. If None (the default), there is no limit.
        :param max_cost: Maximum estimated total cost (f-score) of nodes to explore. If None (the default),
            there is no limit.
        """

        self.neighbor_func = neighbor_func
        self.heuristic = heuristic
        self.max_steps = or_default(max_steps, inf)
        self.max_cost = or_default(max_cost, inf)

        self.stats: AStar.Stats

        self._goal: PathNode
        self._open_set = _OpenSet()
        self._g_scores = DictWithDefault(inf)
        self._closest: PathNode
        self._closest_dist: float
        self._came_from = {}

    def get_path(self, start: PathNode, goal: PathNode, run_limit: RunLimit = None) -> NavPath:
        self._setup(start, goal)

        run_limit = or_default(run_limit, True)

        try:
            steps = 0
            while self._is_searching() and steps < self.max_steps and run_limit:
                steps += 1
                self._step()

            return self._build_path(self._closest)
        finally:
            self._clear()

    def _setup(self, start: PathNode, goal: PathNode) -> None:
        self._clear()

        self.stats = AStar.Stats()

        self._goal = goal
        self._open_set.add_if_not_in(start, 0.)
        self._g_scores[start] = 0.
        self._closest = start
        self._closest_dist = (self.heuristic(start, goal), 0.)

    def _is_searching(self) -> bool:
        return self._closest != self._goal and not self._open_set.is_empty()

    def _step(self):
        current = self._current = self._open_set.pop()
        self.stats.nodes_evaluated += 1
        if current == self._goal:
            self._closest = current
            return

        # Using this tuple ensures the cell closest to the goal will be chosen,
        # and if two cells have the same distance to the goal, then the cell
        # with the lowest g-score (cost to get to) is chosen
        current_dist = (self.heuristic(current, self._goal), self._g_scores[current])
        if current_dist < self._closest_dist:
            self._closest = current
            self._closest_dist = current_dist

        for neighbor, cost in self.neighbor_func(current):
            g_score = self._g_scores[current] + cost
            if g_score >= self._g_scores[neighbor]:
                continue

            f_score = g_score + self.heuristic(neighbor, self._goal)
            if self._cost_is_too_high(f_score):
                continue

            self._came_from[neighbor] = current
            self._g_scores[neighbor] = g_score

            self._open_set.add_if_not_in(neighbor, f_score)

    def _cost_is_too_high(self, cost: float) -> bool:
        return self.max_cost is not None and cost > self.max_cost

    def _build_path(self, to_node: PathNode) -> NavPath:
        current = to_node

        nodes = [current]
        cum_costs = [self._g_scores[current]]

        while current in self._came_from:
            current = self._came_from[current]
            nodes.append(current)
            cum_costs.append(self._g_scores[current])

        nodes.reverse()
        cum_costs.reverse()

        return NavPath(nodes, cum_costs, self._goal)

    def _clear(self) -> None:
        self._open_set.clear()
        self._g_scores.clear()
        self._came_from.clear()

    @dataclass
    class Stats:
        nodes_evaluated: int = 0


class BidirAStar(Nav):
    """
    Bidirectional A* path planning.

    Implementation based on: https://en.wikipedia.org/wiki/A*_search_algorithm#Pseudocode
    """

    def __init__(
            self,
            neighbor_func: Callable[[PathNode], Iterable[Tuple[PathNode, float]]],
            heuristic: Callable[[PathNode, PathNode], float] = euclidean_heuristic,
            max_steps: int = None,
            max_cost: float = None,
            stop_if_no_path: bool = False,
    ):
        """
        :param neighbor_func: For a given node, it should return an iterable of tuples (neighbor, cost).
        :param heuristic: A function that estimates the cost to go from one node to another. Euclidian distance
            (the default) is good for most worlds, as the shortest distance between two points is a straight line.
        :param max_steps: Maximum number of nodes to evaluate before stopping. If None (the default), there is no limit.
        :param max_cost: Maximum estimated total cost (f-score) of nodes to explore. If None (the default),
            there is no limit.
        :param stop_if_no_path: (default: False) if True, then if the backwards search determines there is no path from
            the goal to the start, this will return early with a path from the start to whatever node is the closest to
            the goal, as far as the forward search has seen. If False, then the forwards search will be allowed to keep
            searching until one of the other stopping criteria is reached, allowing it to find a possibly even closer
            node, even though there is no path to the goal node.
        """

        self.max_steps = or_default(max_steps, inf)
        self.stop_if_no_path = stop_if_no_path

        self.stats: Optional[AStar.Stats] = None

        def reverse_heuristic(start_, end_) -> float:
            return heuristic(end_, start_)

        self._goal: PathNode
        self._from_start = AStar(neighbor_func, heuristic, max_cost=max_cost)
        self._from_goal = AStar(neighbor_func, reverse_heuristic, max_cost=max_cost)
        self._middle_node: Optional[PathNode] = None

    def get_path(self, start: PathNode, goal: PathNode, run_limit: RunLimit = None) -> NavPath:
        self._setup(start, goal)

        run_limit = or_default(run_limit, True)

        try:
            steps = 0
            while run_limit and steps < self.max_steps:
                # Search in the forward direction
                self._from_start._step()
                steps += 1
                current = self._from_start._current
                if current in self._from_goal._g_scores:
                    self._middle_node = current
                    break
                if not self._from_start._is_searching():
                    break

                if not self._from_goal._is_searching():
                    if self.stop_if_no_path:
                        break
                    else:
                        continue

                # Search in the backward direction
                self._from_goal._step()
                steps += 1
                current = self._from_goal._current
                if current in self._from_start._g_scores:
                    self._middle_node = current
                    break

            self.stats = AStar.Stats(
                nodes_evaluated=self._from_start.stats.nodes_evaluated + self._from_goal.stats.nodes_evaluated
            )

            return self._build_path()
        finally:
            self._clear()

    def _setup(self, start: PathNode, goal: PathNode) -> None:
        self.stats = None
        self._goal = goal
        self._from_start._setup(start, goal)
        self._from_goal._setup(goal, start)
        self._middle_node = None

    def _build_path(self) -> NavPath:
        if self._middle_node is None:
            return self._from_start._build_path(self._from_start._closest)

        from_start_to_middle = self._from_start._build_path(self._middle_node)

        from_goal_to_middle = self._from_goal._build_path(self._middle_node)

        full_path = [
            *from_start_to_middle.nodes_without_end,
            *reversed(from_goal_to_middle.nodes)
        ]

        cost_from_start_to_middle = from_start_to_middle.cum_costs[-1]
        cost_from_goal_to_middle = from_goal_to_middle.cum_costs[-1]
        cum_costs = list(from_start_to_middle.cum_costs)
        for cost_from_node_to_goal in reversed(from_goal_to_middle.cum_costs[:-1]):
            cum_costs.append(cost_from_start_to_middle + cost_from_goal_to_middle - cost_from_node_to_goal)

        return NavPath(full_path, cum_costs, self._goal)

    def _clear(self) -> None:
        self._from_start._clear()
        self._from_goal._clear()


class _OpenSet:
    __slots__ = ('_heap', '_set')

    def __init__(self):
        self._heap = PriorityQueue()
        self._set = set()

    def add_if_not_in(self, item: PathNode, f_score: float) -> None:
        if item not in self._set:
            self._heap.put(PrioritizedItem(f_score, item))
            self._set.add(item)

    def clear(self) -> None:
        self._heap = PriorityQueue()
        self._set.clear()

    def pop(self) -> PathNode:
        item = self._heap.get_nowait().item
        self._set.remove(item)
        return item

    def is_empty(self) -> bool:
        return not self._set
