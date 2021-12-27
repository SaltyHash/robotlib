import time


class Clock:
    def get_time(self) -> float:
        """
        Returns the time in seconds.

        This may or may not be real, "wall clock" time; it could be simulation time. The only constraint is that it
        must be monotonically increasing (i.e. it will never return a time earlier than any previously-returned time).
        """

        raise NotImplementedError()


class RealTimeClock(Clock):
    def get_time(self):
        """
        Returns the time in real seconds.

        Note that this is not necessarily the actual time-of-day, it is simply a time counter aligned with real seconds.
        """

        return time.monotonic()
