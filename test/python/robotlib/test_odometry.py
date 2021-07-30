import unittest

from robotlib.odometry import DifferentialOdometry
from math import pi


class TestDifferentialOdometryUpdateFromVelocity(unittest.TestCase):
    def assert_odom_equal(self, x: float, y: float, heading: float):
        self.assertAlmostEqual(self.odom.x, x)
        self.assertAlmostEqual(self.odom.y, y)
        self.assertAlmostEqual(self.odom.heading, heading)

    def setUp(self):
        self.odom = DifferentialOdometry(1.0)

    def test_update_result(self):
        expected_keys = {'x', 'd_x', 'y', 'd_y', 'heading', 'd_heading', 'd_t'}

        result = self.odom.update_from_velocity(0, 0, 0)
        actual_keys = set(result.keys())

        self.assertSetEqual(actual_keys, expected_keys)

    def test_update_stopped(self):
        self.odom.update_from_velocity(0, 0, 1)
        self.assert_odom_equal(0, 0, 0)

    def test_update_forward(self):
        self.odom.update_from_velocity(1, 1, 1)
        self.assert_odom_equal(1, 0, 0)

    def test_update_backward(self):
        self.odom.update_from_velocity(-1, -1, 1)
        self.assert_odom_equal(-1, 0, 0)

    def test_update_left(self):
        self.odom.update_from_velocity(-1, 1, 1)
        self.assert_odom_equal(0, 0, 2)

    def test_update_right(self):
        self.odom.update_from_velocity(1, -1, 1)
        self.assert_odom_equal(0, 0, -2)

    def test_update_forward_left(self):
        self.odom.update_from_velocity(0, pi / 2, 1)
        self.assert_odom_equal(0.5, 0.5, pi / 2)

    def test_update_forward_right(self):
        self.odom.update_from_velocity(pi / 2, 0, 1)
        self.assert_odom_equal(0.5, -0.5, -pi / 2)

    def test_update_backward_left(self):
        self.odom.update_from_velocity(0, -pi / 2, 1)
        self.assert_odom_equal(-0.5, 0.5, -pi / 2)

    def test_update_backward_right(self):
        self.odom.update_from_velocity(-pi / 2, 0, 1)
        self.assert_odom_equal(-0.5, -0.5, pi / 2)

    def test_update_detailed(self):
        self.odom = DifferentialOdometry(1.23)
        self.odom.update_from_velocity(0.2, 0.23, 4.5)
        self.assert_odom_equal(0.9655587, 0.0530412, 0.1097561)

    def test_update_multiple(self):
        self.odom.update_from_velocity(1, 1, 1)
        self.assert_odom_equal(1, 0, 0)

        self.odom.update_from_velocity(-1, 1, pi / 2)
        self.assert_odom_equal(1, 0, pi)

        self.odom.update_from_velocity(1, 1, 1)
        self.assert_odom_equal(0, 0, pi)

        self.odom.update_from_velocity(1, -1, pi / 2)
        self.assert_odom_equal(0, 0, 0)


if __name__ == '__main__':
    unittest.main()
