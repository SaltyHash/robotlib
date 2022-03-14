import unittest
from math import pi

from parameterized import parameterized

from robotlib import geometry
from robotlib.geometry import Point2D, Point3D


class AngleFunctionsTest(unittest.TestCase):
    @parameterized.expand([
        # [start_point, end_point, expected_angle]
        [Point2D(0, 0), Point2D(0, 0), 0.0],
        [Point2D(0, 0), Point2D(1, 0), 0.0],
        [Point2D(0, 0), Point2D(1, 1), pi / 4],
        [Point2D(0, 0), Point2D(0, 1), pi / 2],
        [Point2D(0, 0), Point2D(-1, 1), 3 * pi / 4],
        [Point2D(0, 0), Point2D(-1, 0), pi],
        [Point2D(0, 0), Point2D(-1, -1), -3 * pi / 4],
        [Point2D(0, 0), Point2D(0, -1), -pi / 2],
        [Point2D(0, 0), Point2D(1, -1), -pi / 4],
    ])
    def test_angle_between(
            self,
            start_point: Point2D,
            end_point: Point2D,
            expected_angle: float
    ) -> None:
        actual_angle = geometry.angle_between(start_point, end_point)
        self.assertAlmostEqual(expected_angle, actual_angle)

    @parameterized.expand([
        # [start_point, end_point, heading, expected_angle]
        [Point2D(0, 0), Point2D(0, 0), 0.0, 0.0],
        [Point2D(0, 0), Point2D(0, 0), pi / 2, -pi / 2],
        [Point2D(0, 0), Point2D(1, 1), 0.0, pi / 4],
        [Point2D(0, 0), Point2D(1, 1), pi / 4, 0.0],
        [Point2D(0, 0), Point2D(1, 1), -3 * pi / 4, -pi],
    ])
    def test_angle_between_heading(
            self,
            start_point: Point2D,
            end_point: Point2D,
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
        [pi, -pi],
        [-pi, -pi],
        [3 * pi / 2, -pi / 2],
        [-3 * pi / 2, pi / 2],
        [2 * pi, 0.0],
        [-2 * pi, 0.0],
        [5 * pi, -pi],
        [1.1 * pi, -0.9 * pi]
    ])
    def test_trunc_angle(self, angle: float, expected_angle: float) -> None:
        actual_angle = geometry.trunc_angle(angle)
        self.assertAlmostEqual(expected_angle, actual_angle)


class Point2DTest(unittest.TestCase):
    @parameterized.expand([
        # [point, expected_abs]
        [Point2D(0, 0), 0],
        [Point2D(1, 0), 1],
        [Point2D(-1, 0), 1],
        [Point2D(0, 2), 2],
        [Point2D(0, -2), 2],
        [Point2D(2, 3), 3.605551275],
        [Point2D(-4, -9), 9.848857802],
    ])
    def test_abs(self, point: Point2D, expected_abs: float) -> None:
        actual_abs = abs(point)
        self.assertAlmostEqual(expected_abs, actual_abs)

    def test_add(self) -> None:
        point_a = Point2D(x=1, y=2)
        point_b = Point2D(x=4, y=-5)

        point_c = point_a + point_b

        self.assertEqual(5, point_c.x)
        self.assertEqual(-3, point_c.y)

    @parameterized.expand([
        # [point_a, point_b]
        [Point2D(0, 0), Point2D(0, 0)],
        [Point2D(1, 0), Point2D(1, 0)],
        [Point2D(0, -2), Point2D(0, -2)],
        [Point2D(-3, 4), Point2D(-3, 4)],
    ])
    def test_eq__true(self, point_a: Point2D, point_b: Point2D) -> None:
        self.assertEqual(point_a, point_b)

    @parameterized.expand([
        # [point_a, point_b]
        [Point2D(0, 0), Point2D(0, 1)],
        [Point2D(1, 0), Point2D(0, 0)],
        [Point2D(0, -2), Point2D(0, 2)],
        [Point2D(-3, 4), Point2D(-3, -4)],
    ])
    def test_eq__false(self, point_a: Point2D, point_b: Point2D) -> None:
        self.assertNotEqual(point_a, point_b)

    def test_str(self) -> None:
        point = Point2D(x=1.2, y=3.4)

        result = str(point)

        self.assertEqual('<x=1.2, y=3.4>', result)


class Point3DTest(unittest.TestCase):
    @parameterized.expand([
        # [point, expected_abs]
        [Point3D(0, 0, 0), 0],
        [Point3D(1, 0, 0), 1],
        [Point3D(-1, 0, 0), 1],
        [Point3D(0, 2, 0), 2],
        [Point3D(0, -2, 0), 2],
        [Point3D(0, 0, 3), 3],
        [Point3D(0, 0, -3), 3],
        [Point3D(2, 3, 4), 5.385164807],
        [Point3D(-5, -6, -7), 10.488088482],
    ])
    def test_abs(self, point: Point3D, expected_abs: float) -> None:
        actual_abs = abs(point)
        self.assertAlmostEqual(expected_abs, actual_abs)

    def test_add(self) -> None:
        point_a = Point3D(x=1, y=2, z=3)
        point_b = Point3D(x=4, y=-5, z=20)

        point_c = point_a + point_b

        self.assertEqual(5, point_c.x)
        self.assertEqual(-3, point_c.y)
        self.assertEqual(23, point_c.z)

    @parameterized.expand([
        # [point_a, point_b]
        [Point3D(0, 0, 0), Point3D(0, 0, 0)],
        [Point3D(1, 0, 0), Point3D(1, 0, 0)],
        [Point3D(0, -2, 0), Point3D(0, -2, 0)],
        [Point3D(0, 0, 3), Point3D(0, 0, 3)],
        [Point3D(-4, 5, -6), Point3D(-4, 5, -6)],
    ])
    def test_eq__true(self, point_a: Point3D, point_b: Point3D) -> None:
        self.assertEqual(point_a, point_b)

    @parameterized.expand([
        # [point_a, point_b]
        [Point3D(0, 0, 0), Point3D(1, 0, 0)],
        [Point3D(1, 0, 0), Point3D(1, 2, 0)],
        [Point3D(0, -2, 0), Point3D(0, -2, 3)],
        [Point3D(-4, 5, -6), Point3D(-4, 5, 6)],
    ])
    def test_eq__false(self, point_a: Point3D, point_b: Point3D) -> None:
        self.assertNotEqual(point_a, point_b)

    def test_str(self) -> None:
        point = Point3D(x=1.2, y=3.4, z=5.6)

        result = str(point)

        self.assertEqual('<x=1.2, y=3.4, z=5.6>', result)


if __name__ == '__main__':
    unittest.main()
