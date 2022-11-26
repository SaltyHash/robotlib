from unittest import TestCase

import numpy as np
from parameterized import parameterized

from robotlib.viz.color import Color


class ColorTest(TestCase):
    def test_to_array(self):
        color = Color(.1, .2, .3)

        result = color.to_array()

        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_equal(result, [.1, .2, .3])

    def test_to_int8(self):
        color = Color(-.1, .5, 1.5)

        result = color.to_int8()

        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_equal(result, [0, 128, 255])

    def test_to_hex_with_default_prefix(self):
        color = Color(0, 0.5, 1)
        result = color.to_hex()
        self.assertEqual('0x0080FF', result)

    @parameterized.expand([
        [None, ''],
        ['', ''],
        ['0x', '0x'],
        ['#', '#']
    ])
    def test_to_hex_with_prefix(self, prefix: str, expected_prefix: str):
        color = Color(0, 0.5, 1)

        result = color.to_hex(prefix=prefix)

        expected = expected_prefix + '0080FF'
        self.assertEqual(expected, result)

    def test_from_array(self):
        result = Color.from_array(np.array([.1, .2, .3]))
        self.assertEqual(Color(.1, .2, .3), result)

    def test_from_int8(self):
        result = Color.from_int8(0, 128, 255)
        np.testing.assert_almost_equal(result, [0., 0.5019608, 1])

    @parameterized.expand([
        [''],
        ['0x'],
        ['#']
    ])
    def test_from_hex(self, prefix: str):
        result = Color.from_hex(prefix + '0080Ff')
        np.testing.assert_almost_equal(result, [0., 0.5019608, 1])
