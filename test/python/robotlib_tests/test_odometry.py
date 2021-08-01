import unittest

from robotlib import odometry
from math import pi


class DifferentialOdometryUpdateFromVelocityTest(unittest.TestCase):
    def assert_odom_equal(self, x: float, y: float, heading: float):
        self.assertAlmostEqual(self.odom.x, x)
        self.assertAlmostEqual(self.odom.y, y)
        self.assertAlmostEqual(self.odom.heading, heading)

    def setUp(self):
        self.odom = odometry.DifferentialOdometry(1.0)

    def test_update__result(self):
        expected_keys = {'x', 'd_x', 'y', 'd_y', 'heading', 'd_heading', 'd_t'}

        result = self.odom.update_from_velocity(0, 0, 0)
        actual_keys = set(result.keys())

        self.assertSetEqual(actual_keys, expected_keys)

    def test_update__stopped(self):
        self.odom.update_from_velocity(0, 0, 1)
        self.assert_odom_equal(0, 0, 0)

    def test_update__forward(self):
        self.odom.update_from_velocity(1, 1, 1)
        self.assert_odom_equal(1, 0, 0)

    def test_update__backward(self):
        self.odom.update_from_velocity(-1, -1, 1)
        self.assert_odom_equal(-1, 0, 0)

    def test_update__left(self):
        self.odom.update_from_velocity(-1, 1, 1)
        self.assert_odom_equal(0, 0, 2)

    def test_update__right(self):
        self.odom.update_from_velocity(1, -1, 1)
        self.assert_odom_equal(0, 0, -2)

    def test_update__forward_left(self):
        self.odom.update_from_velocity(0, pi / 2, 1)
        self.assert_odom_equal(0.5, 0.5, pi / 2)

    def test_update__forward_right(self):
        self.odom.update_from_velocity(pi / 2, 0, 1)
        self.assert_odom_equal(0.5, -0.5, -pi / 2)

    def test_update__backward_left(self):
        self.odom.update_from_velocity(0, -pi / 2, 1)
        self.assert_odom_equal(-0.5, 0.5, -pi / 2)

    def test_update__backward_right(self):
        self.odom.update_from_velocity(-pi / 2, 0, 1)
        self.assert_odom_equal(-0.5, -0.5, pi / 2)

    def test_update__detailed(self):
        self.odom = odometry.DifferentialOdometry(1.23)
        self.odom.update_from_velocity(0.2, 0.23, 4.5)
        self.assert_odom_equal(0.9655587, 0.0530412, 0.1097561)

    def test_update__multiple(self):
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
