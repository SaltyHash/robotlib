import time


class Clock:
    def get_time(self) -> float:
        """
        Returns the time in seconds.

        This may or may not be real, "wall clock" time; it could be simulation time. The only constraint is that it
        must be monotonically increasing (i.e. it will never return a time earlier than any previously-returned time).
        """

        raise NotImplementedError()

    def sleep(self, secs: float) -> None:
        """Sleep for `secs` seconds."""
        raise NotImplementedError()


class RealTimeClock(Clock):
    def get_time(self):
        """
        Returns the time in real seconds.

        Note that this is not necessarily the actual time-of-day, it is simply a time counter aligned with real seconds.
        """

        return time.monotonic()

    def sleep(self, secs: float) -> None:
        time.sleep(secs)


_RTC = RealTimeClock()


def get_rtc() -> 'RealTimeClock':
    """Returns a singleton instance of the ``RealTimeClock`` class."""
    return _RTC


class SimClock(Clock):
    """Simulated clock. Useful for simulations or testing."""

    def __init__(self, init_time: float = 0.0):
        self._time = init_time

    def get_time(self) -> float:
        return self._time

    def set_time(self, new_time: float) -> None:
        self._validate_time(new_time)
        self._time = new_time

    def _validate_time(self, new_time: float) -> None:
        current_time = self.get_time()
        if new_time < current_time:
            raise ValueError(
                f'New time ({new_time}) cannot be before '
                f'the current time ({current_time}).'
            )

    def inc(self, dt: float) -> None:
        """Increment the time by `dt`."""

        new_time = self.get_time() + dt
        self.set_time(new_time)

    def sleep(self, sleep_time: float) -> None:
        self.inc(sleep_time)


class OffsetClock(Clock):
    """Adds an offset to the time returned by a source clock."""

    def __init__(self, source_clock: 'Clock', offset: float):
        """
        :param source_clock: The clock providing the time.
        :param offset: The amount of time to add to the source clock's time.
        """

        self.source_clock = source_clock
        self.offset = offset

    def get_offset(self) -> float:
        return self.offset

    def set_offset(self, offset: float) -> None:
        self.offset = offset

    def get_time(self) -> float:
        return self.source_clock.get_time() + self.offset

    def sleep(self, secs: float) -> None:
        self.source_clock.sleep(secs)
