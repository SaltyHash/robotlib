import unittest
from typing import Optional
from unittest import TestCase

from parameterized import parameterized

from robotlib.mathutils import Clipper, LinearExtrapolator, Point2d


class TestClipper(TestCase):
    @parameterized.expand([
        # [min_value, max_value, x, expected_y]
        [-5, 10, 0, 0],
        [-5, 10, -4, -4],
        [-5, 10, -5, -5],
        [-5, 10, -6, -5],
        [None, 10, -6, -6],
        [-5, 10, 9, 9],
        [-5, 10, 10, 10],
        [-5, 10, 11, 10],
        [-5, None, 11, 11],
    ])
    def test_clip(
            self,
            min_value: Optional[float],
            max_value: Optional[float],
            x: float,
            expected_y: float
    ) -> None:
        clipper = Clipper(min_value, max_value)

        actual_y = clipper.clip(x)

        self.assertAlmostEqual(expected_y, actual_y)

    def test_call(self) -> None:
        clipper = Clipper(-2, 5)
        x = 10

        clip_result = clipper.clip(x)
        call_result = clipper(x)

        self.assertEqual(clip_result, call_result)

    def test_get_min(self) -> None:
        clipper = Clipper(3, 10)

        actual = clipper.get_min()

        self.assertEqual(3, actual)

    def test_set_min__good_value(self) -> None:
        clipper = Clipper(None, 10)

        clipper.set_min(5)
        actual = clipper.get_min()

        self.assertEqual(5, actual)

    def test_set_min__bad_value__raise_ValueError(self) -> None:
        clipper = Clipper(5, 10)

        with self.assertRaises(ValueError) as assert_context:
            clipper.set_min(20)

        self.assertEqual(
            'Min value (20) cannot be greater than max value (10).',
            str(assert_context.exception)
        )

    def test_get_max(self) -> None:
        clipper = Clipper(3, 10)

        actual = clipper.get_max()

        self.assertEqual(10, actual)

    def test_set_max(self) -> None:
        clipper = Clipper(5, None)

        clipper.set_max(10)
        actual = clipper.get_max()

        self.assertEqual(10, actual)

    def test_set_max__bad_value__raise_ValueError(self) -> None:
        clipper = Clipper(5, 10)

        with self.assertRaises(ValueError) as assert_context:
            clipper.set_max(0)

        self.assertEqual(
            'Max value (0) cannot be greater than min value (5).',
            str(assert_context.exception)
        )


class TestLinearExtrapolator(TestCase):
    @parameterized.expand([
        # [x, expected_y]
        [0, 0],
        # - Positive x
        [1.0, -2],
        [5.0, -10],
        [9.5, -19],
        [10.0, -20],
        [10.5, -20],
        # - Negative x
        [-1, 2],
        [-4.5, 9],
        [-5.0, 10],
        [-5.5, 10]
    ])
    def test_extrapolate(
            self,
            x: float,
            expected_y: float
    ) -> None:
        extrapolator = LinearExtrapolator(
            x0=1,
            y0=-2,
            x1=5,
            y1=-10,
            min_output=-20,
            max_output=10
        )

        actual_y = extrapolator.extrapolate(x)

        self.assertAlmostEqual(expected_y, actual_y)


class TestPoint2d(TestCase):
    def setUp(self) -> None:
        self.a = Point2d(2, -3.)
        self.b = Point2d(-4, 5.)

    def test_abs(self):
        self.assertEqual(Point2d(2, 3), abs(self.a))

    def test_add(self):
        self.assertEqual(Point2d(-2, 2), self.a + self.b)
        self.assertEqual(Point2d(7, 2), self.a + 5)
        self.assertEqual(Point2d(7, 3), self.a + [5, 6])

    def test_radd(self):
        self.assertEqual(Point2d(7, 2), 5 + self.a)
        self.assertEqual(Point2d(7, 3), [5, 6] + self.a)

    def test_sub(self):
        self.assertEqual(Point2d(6, -8), self.a - self.b)
        self.assertEqual(Point2d(-3, -8), self.a - 5)
        self.assertEqual(Point2d(-3, -9), self.a - [5, 6])

    def test_rsub(self):
        self.assertEqual(Point2d(3, 8), 5 - self.a)
        self.assertEqual(Point2d(3, 9), [5, 6] - self.a)

    def test_mul(self):
        self.assertEqual(Point2d(-8, -15), self.a * self.b)
        self.assertEqual(Point2d(10, -15), self.a * 5)
        self.assertEqual(Point2d(10, -18), self.a * [5, 6])

    def test_rmul(self):
        self.assertEqual(Point2d(10, -15), 5 * self.a)
        self.assertEqual(Point2d(10, -18), [5, 6] * self.a)

    def test_truediv(self):
        self.assertEqual(Point2d(2 / -4, -3 / 5), self.a / self.b)
        self.assertEqual(Point2d(2 / 5, -3 / 5), self.a / 5)
        self.assertEqual(Point2d(2 / 5, -3 / 6), self.a / [5, 6])

    def test_rtruediv(self):
        self.assertEqual(Point2d(5 / 2, 5 / -3), 5 / self.a)
        self.assertEqual(Point2d(5 / 2, 6 / -3), [5, 6] / self.a)

    def test_floordiv(self):
        self.assertEqual(Point2d(-1, -1), self.a // self.b)
        self.assertEqual(Point2d(0, -1), self.a // 5)
        self.assertEqual(Point2d(0, -1), self.a // [5, 6])

    def test_rfloordiv(self):
        self.assertEqual(Point2d(2, -2), 5 // self.a)
        self.assertEqual(Point2d(2, -2), [5, 6] // self.a)


if __name__ == '__main__':
    unittest.main()
