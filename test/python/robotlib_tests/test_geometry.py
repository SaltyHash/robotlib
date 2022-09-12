import unittest
from math import pi

from parameterized import parameterized

from robotlib import geometry
from robotlib.geometry import Vector2d, Point3D


class AngleFunctionsTest(unittest.TestCase):
    @parameterized.expand([
        # [start_point, end_point, expected_angle]
        [Vector2d(0, 0), Vector2d(0, 0), 0.0],
        [Vector2d(0, 0), Vector2d(1, 0), 0.0],
        [Vector2d(0, 0), Vector2d(1, 1), pi / 4],
        [Vector2d(0, 0), Vector2d(0, 1), pi / 2],
        [Vector2d(0, 0), Vector2d(-1, 1), 3 * pi / 4],
        [Vector2d(0, 0), Vector2d(-1, 0), pi],
        [Vector2d(0, 0), Vector2d(-1, -1), -3 * pi / 4],
        [Vector2d(0, 0), Vector2d(0, -1), -pi / 2],
        [Vector2d(0, 0), Vector2d(1, -1), -pi / 4],
    ])
    def test_angle_between(
            self,
            start_point: Vector2d,
            end_point: Vector2d,
            expected_angle: float
    ) -> None:
        actual_angle = geometry.angle_between(start_point, end_point)
        self.assertAlmostEqual(expected_angle, actual_angle)

    @parameterized.expand([
        # [start_point, end_point, heading, expected_angle]
        [Vector2d(0, 0), Vector2d(0, 0), 0.0, 0.0],
        [Vector2d(0, 0), Vector2d(0, 0), pi / 2, -pi / 2],
        [Vector2d(0, 0), Vector2d(1, 1), 0.0, pi / 4],
        [Vector2d(0, 0), Vector2d(1, 1), pi / 4, 0.0],
        [Vector2d(0, 0), Vector2d(1, 1), -3 * pi / 4, pi],
    ])
    def test_angle_between_heading(
            self,
            start_point: Vector2d,
            end_point: Vector2d,
            heading: float,
            expected_angle: float
    ) -> None:
        actual_angle = geometry.angle_between_heading(
            start_point, end_point, heading)

        self.assertAlmostEqual(expected_angle, actual_angle)

    @parameterized.expand([
        # [angle, expected_angle]
        [0.0, 0.0],
        [pi / 2, pi / 2],
        [pi, pi],
        [-pi, pi],
        [3 * pi / 2, -pi / 2],
        [-3 * pi / 2, pi / 2],
        [2 * pi, 0.0],
        [-2 * pi, 0.0],
        [5 * pi, pi],
        [1.1 * pi, -0.9 * pi]
    ])
    def test_trunc_angle(self, angle: float, expected_angle: float) -> None:
        actual_angle = geometry.trunc_angle(angle)
        self.assertAlmostEqual(expected_angle, actual_angle)


class TestVector2d(unittest.TestCase):
    def setUp(self) -> None:
        self.a = Vector2d(2, -3.)
        self.b = Vector2d(-4, 5.)

    def test_repr(self):
        self.assertEqual('Vector2d(x=2, y=-3.0)', repr(self.a))

    def test_str(self):
        self.assertEqual('<x=2, y=-3.0>', str(self.a))

    def test_abs(self):
        self.assertEqual(Vector2d(2, 3), abs(self.a))

    def test_add(self):
        self.assertEqual(Vector2d(-2, 2), self.a + self.b)
        self.assertEqual(Vector2d(7, 2), self.a + 5)
        self.assertEqual(Vector2d(7, 3), self.a + [5, 6])

    def test_radd(self):
        self.assertEqual(Vector2d(7, 2), 5 + self.a)
        self.assertEqual(Vector2d(7, 3), [5, 6] + self.a)

    def test_sub(self):
        self.assertEqual(Vector2d(6, -8), self.a - self.b)
        self.assertEqual(Vector2d(-3, -8), self.a - 5)
        self.assertEqual(Vector2d(-3, -9), self.a - [5, 6])

    def test_rsub(self):
        self.assertEqual(Vector2d(3, 8), 5 - self.a)
        self.assertEqual(Vector2d(3, 9), [5, 6] - self.a)

    def test_mul(self):
        self.assertEqual(Vector2d(-8, -15), self.a * self.b)
        self.assertEqual(Vector2d(10, -15), self.a * 5)
        self.assertEqual(Vector2d(10, -18), self.a * [5, 6])

    def test_rmul(self):
        self.assertEqual(Vector2d(10, -15), 5 * self.a)
        self.assertEqual(Vector2d(10, -18), [5, 6] * self.a)

    def test_truediv(self):
        self.assertEqual(Vector2d(2 / -4, -3 / 5), self.a / self.b)
        self.assertEqual(Vector2d(2 / 5, -3 / 5), self.a / 5)
        self.assertEqual(Vector2d(2 / 5, -3 / 6), self.a / [5, 6])

    def test_rtruediv(self):
        self.assertEqual(Vector2d(5 / 2, 5 / -3), 5 / self.a)
        self.assertEqual(Vector2d(5 / 2, 6 / -3), [5, 6] / self.a)

    def test_floordiv(self):
        self.assertEqual(Vector2d(-1, -1), self.a // self.b)
        self.assertEqual(Vector2d(0, -1), self.a // 5)
        self.assertEqual(Vector2d(0, -1), self.a // [5, 6])

    def test_rfloordiv(self):
        self.assertEqual(Vector2d(2, -2), 5 // self.a)
        self.assertEqual(Vector2d(2, -2), [5, 6] // self.a)

    def test_copy(self):
        c = self.a.copy()
        self.assertEqual(self.a, c)
        self.assertIsNot(self.a, c)

        c = self.a.copy(x=123)
        self.assertEqual(Vector2d(123, self.a.y), c)

        c = self.a.copy(y=123)
        self.assertEqual(Vector2d(self.a.x, 123), c)


class TestPoint3d(unittest.TestCase):
    def test_str(self) -> None:
        point = Point3D(x=1.2, y=3.4, z=5.6)
        self.assertEqual('<x=1.2, y=3.4, z=5.6>', str(point))


if __name__ == '__main__':
    unittest.main()
