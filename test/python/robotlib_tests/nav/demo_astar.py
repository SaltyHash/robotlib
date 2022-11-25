import random
from abc import ABC, abstractmethod
from itertools import product
from typing import Iterable, Tuple

import numpy as np

from robotlib.nav import PathNode, NavPath
from robotlib.nav.astar import AStar, BidirAStar
from robotlib.nav.heuristics import euclidean_heuristic
from robotlib.utils import Timer, RuntimeLimit


class GridWorld(ABC):
    def __contains__(self, location) -> bool:
        return self.contains(location)

    @abstractmethod
    def contains(self, location: np.ndarray) -> bool:
        ...

    @abstractmethod
    def is_open(self, location: np.ndarray) -> bool:
        ...

    @abstractmethod
    def can_move(self, start: np.ndarray, end: np.ndarray) -> bool:
        ...

    def get_neighbors(self, location: np.ndarray) -> Iterable[np.ndarray]:
        for neighbor in self._generate_neighbors(location):
            if self.contains(neighbor) \
                    and self.is_open(neighbor) \
                    and self.can_move(location, neighbor):
                yield neighbor

    def _generate_neighbors(self, location: np.ndarray) -> Iterable[np.ndarray]:
        dims = location.shape[0]
        diffs = [-1, 0, 1]
        diffs = [diffs] * dims

        for diff in product(*diffs):
            neighbor = location + diff
            if not all(neighbor == location):
                yield neighbor


class ArrayGridWorld(GridWorld):
    def __init__(self, grid: np.ndarray, diag_allowed: bool = True):
        self.grid = grid.astype(bool)
        self.diag_allowed = diag_allowed

    def contains(self, location: np.ndarray) -> bool:
        return not any(location < 0) and not any(location >= self.grid.shape)

    def is_open(self, location: np.ndarray) -> bool:
        return not self.grid[tuple(location)]

    def can_move(self, start: np.ndarray, end: np.ndarray) -> bool:
        max_dist = 2 ** .5 if self.diag_allowed else 1.
        return euclidean_heuristic(start, end) <= max_dist


class RandomGridWorld(GridWorld):
    def __init__(self, seed=0, obstacle_density: float = 0.2, chunk_size: int = 1, diag_allowed: bool = True):
        self.seed = seed
        self.obstacle_density = obstacle_density
        self.chunk_size = chunk_size
        self.diag_allowed = diag_allowed
        self.r = random.Random()

    def contains(self, location: np.ndarray) -> bool:
        return True

    def is_open(self, location: np.ndarray) -> bool:
        location = tuple(np.array(location) // self.chunk_size)
        self.r.seed(hash(location) + self.seed)
        return self.r.random() > self.obstacle_density

    def can_move(self, start: np.ndarray, end: np.ndarray) -> bool:
        max_dist = 2 ** .5 if self.diag_allowed else 1.
        dist = euclidean_heuristic(start, end)
        if dist > max_dist:
            return False

        is_diag = dist > 1.
        if is_diag:
            corner1 = np.array((start[0], end[1]))
            corner2 = np.array((end[0], start[1]))
            return self.is_open(corner1) or self.is_open(corner2)
        else:
            return True


class GridWorldViz:
    EMPTY = ' '
    OBSTACLE = '▒'

    def __init__(self, grid_world: GridWorld):
        self.grid_world = grid_world

    def print(self, bottom_left, top_right, nav_path: NavPath = None):
        grid_letters = self.get_grid_world_letters(bottom_left, top_right)

        if nav_path is not None:
            self.add_nav_path(bottom_left, nav_path, grid_letters)

        grid_letters = self.add_padding(grid_letters)

        self.render_grid_letters(grid_letters)

    def get_grid_world_letters(self, bottom_left, top_right) -> np.ndarray:
        min_x, min_y = bottom_left
        max_x, max_y = top_right

        grid_letters = np.full((max_y - min_y, max_x - min_x), self.EMPTY)

        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                if not self.grid_world.is_open((x, y)):
                    grid_letters[y - min_y, x - min_x] = self.OBSTACLE

        return grid_letters

    def add_nav_path(self, bottom_left, nav_path: NavPath, grid_letters: np.ndarray):
        min_x, min_y = bottom_left

        def node2coord(node_) -> Tuple[int, int]:
            return node_[1] - min_y, node_[0] - min_x

        def coord_is_in_range(coord_: Tuple[int, int]) -> bool:
            coord_ = np.array(coord_)
            return not np.any(coord_ < 0) and not np.any(coord_ >= grid_letters.shape)

        start = node2coord(nav_path.start)
        if coord_is_in_range(start):
            grid_letters[start] = 'S'

        for node in nav_path.nodes_without_start:
            node = node2coord(node)
            if coord_is_in_range(node):
                assert grid_letters[node] == self.EMPTY
                grid_letters[node] = '*'

        goal = node2coord(nav_path.goal)
        if coord_is_in_range(goal):
            grid_letters[goal] = 'G'

    def add_padding(self, grid_letters: np.ndarray) -> np.ndarray:
        top_char = '▄'
        side_char = '█'
        bottom_char = '▀'

        height = grid_letters.shape[0] + 2
        width = grid_letters.shape[1] + 2

        padded_letters = np.zeros((height, width), dtype=str)

        padded_letters[1:-1, 1:-1] = grid_letters
        padded_letters[0, :] = bottom_char
        padded_letters[1:-1, 0] = padded_letters[1:-1, -1] = side_char
        padded_letters[-1, :] = top_char

        return padded_letters

    def render_grid_letters(self, grid_letters: np.ndarray) -> None:
        grid_letters = grid_letters[::-1]

        for row in range(grid_letters.shape[0]):
            line = ''.join(grid_letters[row])
            print(line)


def main():
    # grid_world = _TestGridWorld()
    grid_world = ArrayGridWorld(np.array([
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 1, 1, 1, 0],
        [0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    ]), diag_allowed=True)

    grid_world = RandomGridWorld(
        # Fun seeds: 3, 19, 34
        seed=1,
        obstacle_density=0.4,
        chunk_size=np.array([2, 1]) * 3,
        diag_allowed=True,
    )

    heuristic = euclidean_heuristic

    def get_neighbors(node: PathNode) -> Iterable[Tuple[PathNode, float]]:
        node = np.array(node)
        for neighbor in grid_world.get_neighbors(node):
            yield tuple(neighbor), heuristic(node, neighbor)

    # nav = AStar(
    nav = BidirAStar(
        neighbor_func=get_neighbors,
        heuristic=heuristic,
        max_steps=None,
        max_cost=None,
        stop_if_no_path=True,
    )

    dist = 100
    while not grid_world.is_open((dist, 0)):
        dist -= 1

    with Timer() as timer, RuntimeLimit(20) as run_limit:
        path = nav.get_path(
            start=(0, 0),
            goal=(dist, 0),
            run_limit=run_limit,
        )
        timer = str(timer)

    print(path)
    print(f'hash(path.nodes) = {hash(path.nodes)}')
    print(nav.stats)
    print(timer)

    path_nodes = [*path.nodes, path.goal]
    min_x = min(n[0] for n in path_nodes)
    min_y = min(n[1] for n in path_nodes)
    max_x = max(n[0] for n in path_nodes)
    max_y = max(n[1] for n in path_nodes)

    GridWorldViz(grid_world).print(
        (min_x, min_y),
        (max_x + 1, max_y + 1),
        nav_path=path
    )


if __name__ == '__main__':
    main()
