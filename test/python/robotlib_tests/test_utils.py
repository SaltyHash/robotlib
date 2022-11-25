import unittest

from robotlib.utils import minmax


class MinmaxTest(unittest.TestCase):
    def setUp(self) -> None:
        self.items = [5, 3, 7, 2, 1, 4, 8, 9, 6]

    def test_iterable(self):
        items = (i for i in self.items)
        result = minmax(items)
        self.assertEqual((1, 9), result)

    def test_args(self):
        result = minmax(*self.items)
        self.assertEqual((1, 9), result)

    def test_no_args_raises_TypeError(self):
        self.assertRaises(TypeError, minmax)

    def test_returns_default_when_iterable_is_empty_and_default_is_given(self):
        default = 'hello there'
        result = minmax([], default=default)
        self.assertEqual(default, result)

    def test_raises_ValueError_when_iterable_is_empty_and_default_is_not_given(self):
        self.assertRaises(ValueError, minmax, [])

    def test_uses_key(self):
        result = minmax(self.items, key=lambda i: (i - 5) ** 2)
        self.assertEqual((5, 1), result)

    def test_prefers_first_in_case_of_ties(self):
        a = [0]
        b = [0]
        c = [1]
        d = [1]

        self.assertIsNot(a, b)
        self.assertIsNot(c, d)

        most_min, most_max = minmax(a, b, c, d)

        self.assertIs(a, most_min)
        self.assertIs(c, most_max)
        self.assertIsNot(b, most_min)
        self.assertIsNot(d, most_max)


if __name__ == '__main__':
    unittest.main()
