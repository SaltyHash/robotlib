import unittest
from unittest import TestCase

from robotlib.control.pid import PID


class TestPID(TestCase):
    def test_set_target(self):
        pid = PID(1, 0, 0)

        pid.set_target(1.23)

        self.assertAlmostEqual(1.23, pid.target)

    def test_set_input(self):
        pid = PID(1, 0, 0)

        pid.set_input(4.56)

        self.assertAlmostEqual(4.56, pid.input)

    def test_get_output_p(self):
        pid = PID(2, 0, 0)
        pid.set_target(10)
        pid.set_input(6)

        output = pid.get_output(dt=1)

        # 2 * (10 - 6)
        expected = 8

        self.assertAlmostEqual(expected, output)

    def test_get_output_i(self):
        pid = PID(0, 2, 0)
        pid.set_target(10)
        dt = 0.1

        # First run
        pid.set_input(6)
        output = pid.get_output(dt)
        expected = 0.8  # 2 * (0.1 * (10 - 6) + 0)
        self.assertAlmostEqual(expected, output)

        # Second run
        pid.set_input(8)
        output = pid.get_output(dt)
        expected = 1.2  # 2 * (0.1 * (10 - 8) + 0.1 * (10 - 6))
        self.assertAlmostEqual(expected, output)

    def test_get_output_d(self):
        pid = PID(0, 0, 0.1)
        pid.set_target(10)
        dt = 0.5

        # First run
        pid.set_input(4)
        output = pid.get_output(dt)
        expected = 1.2  # 0.1 * ([(10 - 4) - 0] / 0.5)
        self.assertAlmostEqual(expected, output)

        # Second run
        pid.set_input(8)
        output = pid.get_output(dt)
        expected = -0.8  # 0.1 * ([(10 - 8) - (10 - 4)] / 0.5)
        self.assertAlmostEqual(expected, output)

    def test_get_error(self):
        pid = PID(1, 0, 0)
        pid.set_target(5)
        pid.set_input(3)

        error = pid.get_error()

        self.assertAlmostEqual(2, error)

    def test_output_gain(self):
        pid = PID(1, 0, 0, output_gain=-2)
        pid.set_target(1)
        pid.set_input(0)

        output = pid.get_output(1)

        expected = -2   # -2 * (1 * (1 - 0))
        self.assertAlmostEqual(expected, output)

    def test_min_output(self):
        pid = PID(1, 0, 0, min_output=-5)
        pid.set_target(-10),
        pid.set_input(0)

        output = pid.get_output(1)

        expected = -5
        self.assertAlmostEqual(expected, output)

    def test_max_output(self):
        pid = PID(1, 0, 0, max_output=5)
        pid.set_target(10),
        pid.set_input(0)

        output = pid.get_output(1)

        expected = 5
        self.assertAlmostEqual(expected, output)


if __name__ == '__main__':
    unittest.main()
