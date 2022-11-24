from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Protocol, Any


class Nav(ABC):
    @abstractmethod
    def get_path(self, start: 'PathNode', goal: 'PathNode') -> 'NavPath':
        ...


class NavPath:
    """Represents a navigable path, from start node to end node."""

    def __init__(
            self,
            nodes: Iterable['PathNode'],
            cum_costs: Iterable[float],
            goal: 'PathNode',
    ):
        self.nodes = tuple(nodes)
        self.cum_costs = tuple(cum_costs)
        self.goal = goal

        self.is_complete = self.end == goal

        inc_costs = [0.]
        for i in range(1, len(self.cum_costs)):
            inc_costs.append(self.cum_costs[i] - self.cum_costs[i - 1])
        self.inc_costs = tuple(inc_costs)

        self.total_cost = self.cum_costs[-1]

    @property
    def start(self) -> 'PathNode':
        return self.nodes[0]

    @property
    def end(self) -> 'PathNode':
        return self.nodes[-1]

    @property
    def nodes_without_start(self) -> Tuple['PathNode']:
        return self.nodes[1:]

    @property
    def nodes_without_end(self) -> Tuple['PathNode']:
        return self.nodes[:-1]

    @property
    def nodes_without_ends(self) -> Tuple['PathNode']:
        return self.nodes[1:-1]

    def __iter__(self) -> Iterable[Tuple['PathNode', float, float]]:
        yield from zip(self.nodes, self.cum_costs, self.inc_costs)

    def __len__(self) -> int:
        return len(self.nodes)

    def __str__(self) -> str:
        lines = []

        for i, (node, cum_cost, inc_cost) in enumerate(self):
            if i == 0:
                prefix = '[Start]'
            elif i == len(self) - 1:
                prefix = '[End]  '
            else:
                prefix = '       '

            lines.append(f'{prefix} {i:2d}: {node}; cum_cost={cum_cost:.3f}; inc_cost={inc_cost:.3f}')

        lines.append(f'total_cost={self.total_cost}')
        lines.append(f'is_complete={self.is_complete}')

        return '\n'.join(lines)


class PathNode(Protocol):
    def __eq__(self, other: Any) -> bool: ...

    def __hash__(self) -> int: ...
