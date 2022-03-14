import unittest
from math import pi

from parameterized import parameterized

from robotlib import geometry
from robotlib.geometry import Point2D, Point3D


class GeometryAngleFunctionsTest(unittest.TestCase):
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
        print('actual = ' + str(actual_angle))
        self.assertAlmostEqual(expected_angle, actual_angle)


class GeometryPoint2DTest(unittest.TestCase):
    def test_add(self) -> None:
        point_a = Point2D(x=1, y=2)
        point_b = Point2D(x=4, y=-5)

        point_c = point_a + point_b

        self.assertEqual(5, point_c.x)
        self.assertEqual(-3, point_c.y)

    def test_str(self) -> None:
        point = Point2D(x=1.2, y=3.4)

        result = str(point)

        self.assertEqual('<x=1.2, y=3.4>', result)


class GeometryPoint3DTest(unittest.TestCase):
    def test_add(self) -> None:
        point_a = Point3D(x=1, y=2, z=3)
        point_b = Point3D(x=4, y=-5, z=20)

        point_c = point_a + point_b

        self.assertEqual(5, point_c.x)
        self.assertEqual(-3, point_c.y)
        self.assertEqual(23, point_c.z)

    def test_str(self) -> None:
        point = Point3D(x=1.2, y=3.4, z=5.6)

        result = str(point)

        self.assertEqual('<x=1.2, y=3.4, z=5.6>', result)


if __name__ == '__main__':
    unittest.main()
