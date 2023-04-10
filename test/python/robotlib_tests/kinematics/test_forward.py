import unittest
from math import pi
from typing import Iterable
from unittest import TestCase

from parameterized import parameterized

from robotlib.geometry import Point2d
from robotlib.kinematics.forward import ForwardSolver
from robotlib.kinematics.system import System


class ForwardSolverTest(TestCase):
    def setUp(self) -> None:
        self.target = ForwardSolver()

    @parameterized.expand([
        (Point2d(0, 0), 0., 1., Point2d(1., 0)),
        (Point2d(0.25, 0.5), 0., 1., Point2d(1.25, 0.5)),
        (Point2d(0.25, 0.5), 0., 2., Point2d(2.25, 0.5)),
        (Point2d(0.25, 0.5), pi / 2, 2., Point2d(0.25, 2.5)),
        (Point2d(0.25, 0.5), pi, 2., Point2d(-1.75, 0.5)),
        (Point2d(0.25, 0.5), -pi, 2., Point2d(-1.75, 0.5)),
    ])
    def test_single_link(
            self,
            base_point: Point2d,
            joint_angle: float,
            link_length: float,
            expected_point: Point2d
    ):
        system = System(
            joints=[joint_angle],
            links=[link_length],
        )

        result = self.target.forward(system, base_point=base_point)

        expected = [base_point, expected_point]

        self.assert_points_almost_equal(expected, result)

    def test_double_link(self):
        system = System(
            joints=(pi / 4, -pi / 2),
            links=(2, 3),
        )

        result = self.target.forward(system)

        expected = [
            Point2d(0, 0),
            Point2d(1.414213562, 1.414213562),
            Point2d(3.535533906, -0.707106781),
        ]

        self.assert_points_almost_equal(expected, result)

    def assert_points_almost_equal(
            self,
            expected: Iterable[Point2d],
            actual: Iterable[Point2d],
            epsilon: float = 1e-9
    ) -> None:
        for point_a, point_b in zip(expected, actual):
            diff = abs(point_a - point_b)
            if diff.x > epsilon or diff.y > epsilon:
                raise AssertionError(
                    f'diff {diff} between points {point_a} and {point_b} '
                    f'has at one component with diff > epsilon {epsilon}'
                )


if __name__ == '__main__':
    unittest.main()
