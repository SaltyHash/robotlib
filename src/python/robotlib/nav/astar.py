import math
from queue import PriorityQueue
from typing import Callable, Iterable, Tuple

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
        self.neighbor_func = neighbor_func
        self.heuristic = heuristic
        self.max_steps = or_default(max_steps, math.inf)
        self.max_cost = or_default(max_cost, math.inf)

    def get_path(self, start: PathNode, end: PathNode, run_limit: RunLimit = None) -> NavPath:
        self._setup(start, end)

        run_limit = or_default(run_limit, True)

        steps = 0
        while self._open_set and steps < self.max_steps and run_limit:
            steps += 1

            current = self._open_set.pop()
            if current == self._end:
                self._closest = current
                break

            # Using this tuple ensures the cell closest to the end will be chosen,
            # and if two cells have the same distance to the end, then the cell
            # with the lowest g-score (cost to get to) is chosen
            current_dist = (self.heuristic(current, self._end), self._g_scores[current])
            if current_dist < self._closest_dist:
                self._closest = current
                self._closest_dist = current_dist

            for neighbor, cost in self.neighbor_func(current):
                g_score = self._g_scores[current] + cost
                if g_score >= self._g_scores[neighbor]:
                    continue

                f_score = g_score + self.heuristic(neighbor, self._end)
                if self._cost_is_too_high(f_score):
                    continue

                self._came_from[neighbor] = current
                self._g_scores[neighbor] = g_score

                self._open_set.add_if_not_in(neighbor, f_score)

        try:
            return self._build_path()
        finally:
            self._cleanup()

    def _setup(self, start: PathNode, end: PathNode) -> None:
        self._end = end

        self._open_set = _OpenSet()
        self._open_set.add_if_not_in(start, 0.)

        # Lowest cost to get to each node
        self._g_scores = DictWithDefault(math.inf)
        self._g_scores[start] = 0.

        self._closest = start
        self._closest_dist = (self.heuristic(start, end), 0.)

        self._came_from = {}

    def _cost_is_too_high(self, cost: float) -> bool:
        return self.max_cost is not None and cost > self.max_cost

    def _build_path(self) -> NavPath:
        current = self._closest

        nodes = [current]
        cum_costs = [self._g_scores[current]]

        while current in self._came_from:
            current = self._came_from[current]
            nodes.append(current)
            cum_costs.append(self._g_scores[current])

        nodes.reverse()
        cum_costs.reverse()

        return NavPath(nodes, cum_costs, is_complete=self._closest == self._end)

    def _cleanup(self) -> None:
        self._open_set = None
        self._g_scores = None


class _OpenSet:
    def __init__(self):
        self._heap = PriorityQueue()
        self._set = set()

    def __len__(self) -> int:
        return len(self._set)

    def add_if_not_in(self, item: PathNode, f_score: float) -> None:
        if item not in self._set:
            self._heap.put(PrioritizedItem(f_score, item))
            self._set.add(item)

    def pop(self) -> PathNode:
        item = self._heap.get_nowait().item
        self._set.remove(item)
        return item

    def is_empty(self) -> bool:
        return not self._set
