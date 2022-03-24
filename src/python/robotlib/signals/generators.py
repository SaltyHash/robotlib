import math
from abc import ABC
from math import pi
from typing import Iterator


class SignalGenerator(ABC):
    def sample(self, dt: float) -> float:
        raise NotImplementedError()

    def sample_iter(
            self,
            dt: float,
            sample_count: int = None
    ) -> Iterator[float]:
        """"""
        if sample_count is None:
            yield from self._sample_forever(dt)
        else:
            yield from self._sample_count(dt, sample_count)

    def _sample_forever(self, dt: float) -> Iterator[float]:
        while True:
            yield self.sample(dt)

    def _sample_count(self, dt: float, sample_count: int) -> Iterator[float]:
        for _ in range(sample_count):
            yield self.sample(dt)


class PeriodicSignalGenerator(SignalGenerator, ABC):
    """A signal that repeats periodically."""

    def __init__(self, freq: float = None, period: float = None):
        """
        :param freq: Frequency of the signal. Must be given if period is not.
        :param period: Period of the signal. Must be given if freq is not.
        """

        # Make sure one and only one of freq or period is set
        if freq is None and period is None:
            raise ValueError('Either freq or period must be given.')
        if freq is not None and period is not None:
            raise ValueError(
                'Only one of freq or period should be given, not both.')

        # Set the freq with freq or period
        self._freq = None
        if freq is not None:
            self.set_freq(freq)
        elif period is not None:
            self.set_period(period)
        else:
            raise RuntimeError('This should never be reached.')

        self._t = 0.0

    def get_freq(self) -> float:
        return self._freq

    def set_freq(self, freq: float) -> None:
        self._validate_freq(freq)
        self._freq = freq

    def get_period(self) -> float:
        return 1.0 / self.get_freq()

    def set_period(self, period: float) -> None:
        freq = 1.0 / period
        self.set_freq(freq)

    def _validate_freq(self, freq: float) -> None:
        if freq < 0:
            raise ValueError(f'freq must be >= 0; got {freq}.')

    def sample(self, dt: float) -> float:
        self._update_time(dt)
        return self._get_sample()

    def _update_time(self, dt: float) -> None:
        self._t += dt

    def _get_sample(self) -> float:
        raise NotImplementedError()


class SineWaveGenerator(PeriodicSignalGenerator):
    def _get_sample(self) -> float:
        return math.sin(2 * pi * self._freq * self._t)


class SquareWaveGenerator(PeriodicSignalGenerator):
    """Alternates between outputting a 1.0 and a 0.0."""

    def __init__(
            self,
            freq: float = None,
            period: float = None,
            duty_cycle: float = 0.5
    ):
        """
        :param duty_cycle: The fraction of the period during which the output
            is 1.0. Should be in range [0.0, 1.0]. Defaults to 0.5 (50%).
        """
        super().__init__(freq=freq, period=period)

        self._duty_cycle = None
        self.set_duty_cycle(duty_cycle)

    def get_duty_cycle(self) -> float:
        return self._duty_cycle

    def set_duty_cycle(self, duty_cycle: float) -> None:
        self._validate_duty_cycle(duty_cycle)
        self._duty_cycle = duty_cycle

    def _validate_duty_cycle(self, duty_cycle: float) -> None:
        if duty_cycle < 0.0 or duty_cycle > 1.0:
            raise ValueError(
                f'duty_cycle must be in range [0.0, 1.0]; got {duty_cycle}.')

    def _get_sample(self) -> float:
        period_fraction = self._get_period_fraction()
        duty_cycle = self.get_duty_cycle()
        return 1.0 if period_fraction < duty_cycle else 0.0

    def _get_period_fraction(self) -> float:
        period = self.get_period()
        t_in_period = self._t % period
        fraction = t_in_period / period
        return fraction


class TriangleWaveGenerator(PeriodicSignalGenerator):
    def _get_sample(self) -> float:
        raise NotImplementedError()
