import unittest
from typing import Iterable, Tuple

import numpy as np

from robotlib.nav import PathNode
from robotlib.nav.astar import AStar
from robotlib.nav.heuristics import euclidean_heuristic
from robotlib_tests.nav.demo_astar import ArrayGridWorld


class AStarTest(unittest.TestCase):
    def setUp(self) -> None:
        self.heuristic = euclidean_heuristic
        self.world = ...

    def get_neighbors(self, node: PathNode) -> Iterable[Tuple[PathNode, float]]:
        node = np.array(node)
        for neighbor in self.world.get_neighbors(node):
            yield tuple(neighbor), self.heuristic(node, neighbor)

    def test_small__diagonal_not_allowed(self):
        self.world = ArrayGridWorld(np.array([
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
        ]), diag_allowed=False)

        target = AStar(self.get_neighbors)

        result = target.get_path((2, 0), (2, 2))

        self.assertTrue(result.is_complete)

        expected_nodes = [
            (2, 0),
            (1, 0),
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 2),
            (2, 2),
        ]
        np.testing.assert_equal(result.nodes, expected_nodes)

        expected_cum_costs = [0, 1, 2, 3, 4, 5, 6]
        np.testing.assert_equal(result.cum_costs, expected_cum_costs)

    def test_small__diagonal_allowed(self):
        self.world = ArrayGridWorld(np.array([
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
        ]), diag_allowed=True)

        target = AStar(self.get_neighbors)

        result = target.get_path((2, 0), (2, 2))

        self.assertTrue(result.is_complete)

        expected_nodes = [
            (2, 0),
            (1, 0),
            (0, 1),
            (1, 2),
            (2, 2),
        ]
        np.testing.assert_equal(result.nodes, expected_nodes)

        s = np.sqrt(2)
        expected_cum_costs = [
            0 + 0 * s,
            1 + 0 * s,
            1 + 1 * s,
            1 + 2 * s,
            2 + 2 * s,
        ]
        np.testing.assert_almost_equal(result.cum_costs, expected_cum_costs)

    def test_small__no_path(self):
        self.world = ArrayGridWorld(np.array([
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
        ]), diag_allowed=True)

        target = AStar(self.get_neighbors)

        result = target.get_path((2, 0), (1, 2))

        self.assertFalse(result.is_complete)

        expected_nodes = [
            (2, 0),
            (1, 0),
        ]
        np.testing.assert_equal(result.nodes, expected_nodes)

        expected_cum_costs = [0, 1]
        np.testing.assert_equal(result.cum_costs, expected_cum_costs)

    def test_large(self):
        self.world = ArrayGridWorld(np.array([
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 1, 1, 1, 1, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]), diag_allowed=False)

        target = AStar(self.get_neighbors)

        result = target.get_path((0, 0), (0, 9))

        self.assertTrue(result.is_complete)

        expected_nodes = [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0),
            (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9),
            (5, 9), (4, 9), (3, 9), (2, 9), (1, 9), (0, 9)
        ]

        np.testing.assert_equal(result.nodes, expected_nodes)

        expected_cum_costs = list(range(len(expected_nodes)))
        np.testing.assert_equal(result.cum_costs, expected_cum_costs)


if __name__ == '__main__':
    unittest.main()
