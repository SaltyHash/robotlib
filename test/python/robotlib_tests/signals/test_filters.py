from unittest import TestCase
from math import pi

from robotlib.signals.filters import LowPassFilter, HighPassFilter


class TestLowPassFilter(TestCase):
    def test_set_cutoff_freq__0__good(self):
        f = LowPassFilter(1)
        f.set_cutoff_freq(0)

    def test_set_cutoff_freq__10__good(self):
        f = LowPassFilter(1)
        f.set_cutoff_freq(10)

    def test_set_cutoff_freq__less_than_0__raises_ValueError(self):
        f = LowPassFilter(1)

        with self.assertRaises(ValueError):
            f.set_cutoff_freq(-0.01)

    def test_filter__cutoff_freq_0(self):
        f = LowPassFilter(0)

        output = f.filter(1, 0.1)
        self.assertAlmostEqual(0.0, output)

        output = f.filter(1, 0.1)
        self.assertAlmostEqual(0.0, output)

    def test_filter__simple(self):
        f = LowPassFilter(1)

        # This special dt will make alpha = 0.5
        dt = 1 / (2 * pi)

        output = f.filter(1, dt)
        self.assertAlmostEqual(0.5, output)

        output = f.filter(1, dt)
        self.assertAlmostEqual(0.75, output)

        output = f.filter(1, dt)
        self.assertAlmostEqual(0.875, output)

    def test_filter__complex(self):
        f = LowPassFilter(120)
        dt = 1 / 44100

        output = f.filter(0.23, dt)
        self.assertAlmostEqual(0.0038662, output)

        output = f.filter(0.34, dt)
        self.assertAlmostEqual(0.0095165, output)


class TestHighPassFilter(TestCase):
    def test_set_cutoff_freq__0__good(self):
        f = HighPassFilter(1)
        f.set_cutoff_freq(0)

    def test_set_cutoff_freq__10__good(self):
        f = HighPassFilter(1)
        f.set_cutoff_freq(10)

    def test_set_cutoff_freq__less_than_0__raises_ValueError(self):
        f = HighPassFilter(1)

        with self.assertRaises(ValueError):
            f.set_cutoff_freq(-0.01)

    def test_filter__cutoff_freq_0(self):
        f = HighPassFilter(0)

        output = f.filter(1, 0.1)
        self.assertAlmostEqual(1.0, output)

        output = f.filter(0.5, 0.1)
        self.assertAlmostEqual(0.5, output)

    def test_filter__simple(self):
        f = HighPassFilter(1)

        # This special dt will make alpha = 0.5
        dt = 1 / (2 * pi)

        output = f.filter(1, dt)
        self.assertAlmostEqual(0.5 / 1, output)

        output = f.filter(1, dt)
        self.assertAlmostEqual(0.25, output)

        output = f.filter(1, dt)
        self.assertAlmostEqual(0.125, output)

    def test_filter__complex(self):
        f = HighPassFilter(120)
        dt = 1 / 44100

        output = f.filter(0.23, dt)
        self.assertAlmostEqual(0.2261338, output)

        output = f.filter(0.34, dt)
        self.assertAlmostEqual(0.3304835, output)
