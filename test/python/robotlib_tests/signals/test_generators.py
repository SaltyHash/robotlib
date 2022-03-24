import unittest
from typing import Iterator
from unittest import TestCase

from robotlib.signals.generators import SignalGenerator, SineWaveGenerator, \
    PeriodicSignalGenerator, SquareWaveGenerator


class SignalGeneratorImpl(SignalGenerator):
    def __init__(self, samples):
        self.samples = samples
        self.i = 0

    def sample(self, dt: float) -> float:
        sample = self.samples[self.i]

        self.i += 1
        if self.i >= len(self.samples):
            self.i = 0

        return sample


class TestSignalGenerator(TestCase):
    def test_sample(self):
        gen = SignalGeneratorImpl([2, 4, 7])

        result = gen.sample(0.1)
        self.assertEqual(2, result)

        result = gen.sample(0.1)
        self.assertEqual(4, result)

        result = gen.sample(0.1)
        self.assertEqual(7, result)

        result = gen.sample(0.1)
        self.assertEqual(2, result)

    def test_sample_iter__returns_iterator(self):
        gen = SignalGeneratorImpl([2, 4, 7])

        result = gen.sample_iter(0.1)

        self.assertIsInstance(result, Iterator)

    def test_sample_iter__sample_count_int(self):
        gen = SignalGeneratorImpl([2, 4, 7])

        result = list(gen.sample_iter(0.1, 8))

        self.assertListEqual([2, 4, 7, 2, 4, 7, 2, 4], result)

    def test_sample_iter__sample_count_None(self):
        gen = SignalGeneratorImpl([2, 4, 7])

        sample_iter = gen.sample_iter(0.1)

        self.assertEqual(2, next(sample_iter))
        self.assertEqual(4, next(sample_iter))
        self.assertEqual(7, next(sample_iter))
        self.assertEqual(2, next(sample_iter))
        self.assertEqual(4, next(sample_iter))
        self.assertEqual(7, next(sample_iter))


class PeriodicSignalGeneratorImpl(PeriodicSignalGenerator):
    def sample(self, dt: float) -> float:
        return 0.0


class TestPeriodicSignalGenerator(TestCase):
    def test_init__with_freq(self):
        PeriodicSignalGeneratorImpl(freq=42)

    def test_init__with_period(self):
        PeriodicSignalGeneratorImpl(period=0.24)

    def test_init__no_args__raises_ValueError(self):
        with self.assertRaises(ValueError):
            PeriodicSignalGeneratorImpl()

    def test_init__with_freq_and_period__raises_ValueError(self):
        with self.assertRaises(ValueError):
            PeriodicSignalGeneratorImpl(freq=42, period=0.24)

    def test_get_freq(self):
        gen = PeriodicSignalGeneratorImpl(42)

        result = gen.get_freq()

        self.assertEqual(42, result)

    def test_set_freq_and_get_freq(self):
        gen = PeriodicSignalGeneratorImpl(42)

        gen.set_freq(43)
        result = gen.get_freq()

        self.assertEqual(43, result)

    def test_get_period(self):
        gen = PeriodicSignalGeneratorImpl(10)

        result = gen.get_period()

        self.assertAlmostEqual(0.1, result)

    def test_set_period_and_get_period(self):
        gen = PeriodicSignalGeneratorImpl(0)

        gen.set_period(0.123)
        result = gen.get_period()

        self.assertAlmostEqual(0.123, result)


class TestSineWaveGenerator(TestCase):
    def test_sample(self):
        gen = SineWaveGenerator(10)
        dt = (1 / 10) / 8  # 1/8th of a period

        result = gen.sample(0)
        self.assertAlmostEqual(0.0, result)

        result = gen.sample(dt)
        self.assertAlmostEqual(0.707, result, places=3)

        result = gen.sample(dt)
        self.assertAlmostEqual(1.0, result)

        result = gen.sample(dt)
        self.assertAlmostEqual(0.707, result, places=3)

        result = gen.sample(dt)
        self.assertAlmostEqual(0.0, result)


class TestSquareWaveGenerator(TestCase):
    def test_sample(self):
        gen = SquareWaveGenerator(freq=10, duty_cycle=0.5)
        dt = 0.025  # 1/4th of a period

        # 0% of period
        result = gen.sample(0.0)
        self.assertAlmostEqual(1.0, result)

        # 25% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(1.0, result)

        # (50 - e)% of period, i.e. right before the end of the duty cycle
        result = gen.sample(dt - 0.001)
        self.assertAlmostEqual(1.0, result)

        # 50% of period, i.e. the end of the duty cycle
        result = gen.sample(0.001)
        self.assertAlmostEqual(0.0, result)

        # 75% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(0.0, result)

        # 100% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(1.0, result)

    def test_sample__duty_cycle_0__always_0(self):
        gen = SquareWaveGenerator(freq=1, duty_cycle=0.0)
        dt = 0.33  # 33% of period

        # 0% of period
        result = gen.sample(0.0)
        self.assertAlmostEqual(0.0, result)

        # 33% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(0.0, result)

        # 66% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(0.0, result)

        # 99% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(0.0, result)

        # 132% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(0.0, result)

    def test_sample__duty_cycle_1__always_1(self):
        gen = SquareWaveGenerator(freq=1, duty_cycle=1.0)
        dt = 0.33  # 33% of period

        # 0% of period
        result = gen.sample(0.0)
        self.assertAlmostEqual(1.0, result)

        # 33% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(1.0, result)

        # 66% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(1.0, result)

        # 99% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(1.0, result)

        # 132% of period
        result = gen.sample(dt)
        self.assertAlmostEqual(1.0, result)


if __name__ == '__main__':
    unittest.main()
