import unittest
from unittest import TestCase

from robotlib.clocks import RealTimeClock, SimClock, OffsetClock


class TestRealTimeClock(TestCase):
    def test_get_time_and_sleep(self):
        clock = RealTimeClock()

        t0 = clock.get_time()
        clock.sleep(0.1)
        t1 = clock.get_time()

        dt = t1 - t0

        self.assertAlmostEqual(0.1, dt, places=2)


class TestFakeClock(TestCase):
    def test_get_time_and_sleep(self):
        clock = SimClock(init_time=2.0)

        t0 = clock.get_time()
        clock.sleep(1.2)
        t1 = clock.get_time()

        self.assertAlmostEqual(2.0, t0)
        self.assertAlmostEqual(3.2, t1)

    def test_set_time__forward__good(self):
        clock = SimClock()
        t0 = clock.get_time()

        clock.set_time(t0 + 2.3)

    def test_set_time__backward__bad(self):
        clock = SimClock()
        t0 = clock.get_time()

        with self.assertRaises(ValueError):
            clock.set_time(t0 - 2.3)

    def test_inc(self):
        clock = SimClock(init_time=2.0)

        t0 = clock.get_time()
        clock.inc(1.2)
        t1 = clock.get_time()

        self.assertAlmostEqual(2.0, t0)
        self.assertAlmostEqual(3.2, t1)


class TestOffsetClock(TestCase):
    def test_offset_and_sleep(self):
        init_time = 1.2
        source_clock = SimClock(init_time=init_time)
        offset = 3.4
        offset_clock = OffsetClock(source_clock, offset)

        self.assertAlmostEqual(init_time + offset, offset_clock.get_time())

        sleep_time = 5.6
        offset_clock.sleep(sleep_time)

        self.assertAlmostEqual(
            init_time + sleep_time + offset,
            offset_clock.get_time()
        )


if __name__ == '__main__':
    unittest.main()
