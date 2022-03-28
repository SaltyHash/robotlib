import math
import random
from abc import ABC
from math import pi
from typing import Iterator, List

from robotlib.clocks import Clock, get_rtc


class SignalGenerator(Iterator[float], ABC):
    def __iter__(self) -> Iterator[float]:
        return self

    def __next__(self) -> float:
        return self.sample()

    def sample(self) -> float:
        """Returns a single sample."""
        raise NotImplementedError()

    def sample_count(self, sample_count: int) -> Iterator[float]:
        """Yields a certain number of samples."""
        for _ in range(sample_count):
            yield self.sample()


class TimeDependentSignalGenerator(SignalGenerator, ABC):
    def __init__(self, clock: Clock = None):
        self._clock = clock or get_rtc()

    @property
    def _t(self) -> float:
        """The current time."""
        return self._clock.get_time()


class PeriodicSignalGenerator(TimeDependentSignalGenerator, ABC):
    """A signal that repeats periodically."""

    def __init__(
            self,
            freq: float = None,
            period: float = None,
            clock: Clock = None
    ):
        """
        :param freq: Frequency of the signal. Must be given if period is not.
        :param period: Period of the signal. Must be given if freq is not.
        """

        super().__init__(clock)

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

    def _get_period_fraction(self) -> float:
        period = self.get_period()
        t_in_period = self._t % period
        fraction = t_in_period / period
        return fraction


class SineWaveGenerator(PeriodicSignalGenerator):
    def sample(self) -> float:
        return math.sin(2 * pi * self._freq * self._t)


class PeriodicSignalGeneratorWithDutyCycle(PeriodicSignalGenerator, ABC):
    def __init__(
            self,
            freq: float = None,
            period: float = None,
            duty_cycle: float = 0.5,
            clock: Clock = None
    ):
        """
        :param duty_cycle: The fraction of the period during which the output
            is 1.0. Should be in range [0.0, 1.0]. Defaults to 0.5 (50%).
        """

        super().__init__(freq=freq, period=period, clock=clock)

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

    def _is_in_duty_cycle(self) -> bool:
        period_fraction = self._get_period_fraction()
        duty_cycle = self.get_duty_cycle()
        return period_fraction < duty_cycle


class SquareWaveGenerator(PeriodicSignalGeneratorWithDutyCycle):
    """Alternates between outputting a 1.0 and a 0.0."""

    def sample(self) -> float:
        return 1.0 if self._is_in_duty_cycle() else 0.0


class TriangleWaveGenerator(PeriodicSignalGeneratorWithDutyCycle):
    def sample(self) -> float:
        if self._is_in_duty_cycle():
            return self._get_upswing()
        else:
            return self._get_downswing()

    def _get_upswing(self) -> float:
        period_fraction = self._get_period_fraction()
        duty_cycle_fraction = period_fraction / self.get_duty_cycle()
        return duty_cycle_fraction

    def _get_downswing(self) -> float:
        remaining_period_fraction = 1.0 - self._get_period_fraction()
        off_cycle = 1.0 - self.get_duty_cycle()
        return remaining_period_fraction / off_cycle


class RandomSignalGenerator(SignalGenerator, ABC):
    def __init__(
            self,
            seed: int = None,
            randomness: str = 'pseudo'
    ):
        """
        :param seed: Optional seed for the RNG. Only applicable if randomness
            is set to 'pseudo'.
        :param randomness: Either 'pseudo' (the default) or 'true'.
        """

        self._set_rng(randomness)

        if seed is not None:
            self._rng.seed(seed)

    def _set_rng(self, randomness: str) -> None:
        if randomness == 'pseudo':
            self._rng = random.Random()
        elif randomness == 'true':
            self._rng = random.SystemRandom()
        else:
            raise ValueError(
                f'randomness must be either "pseudo" or "true"; '
                f'got {randomness!r}.'
            )


class UniformRandomSignalGenerator(RandomSignalGenerator):
    """Generates a random signal uniformly over the range [low, high)."""

    def __init__(
            self,
            low: float = 0.0,
            high: float = 1.0,
            seed: int = None,
            randomness: str = 'pseudo'
    ):
        super().__init__(seed, randomness)

        self.low = low
        self.high = high

    def sample(self) -> float:
        return self._rng.uniform(self.low, self.high)


class GaussianRandomSignalGenerator(RandomSignalGenerator):
    """Generates a random signal sampled from a Gaussian distribution."""

    def __init__(
            self,
            mean: float = 0.0,
            std_dev: float = 1.0,
            seed: int = None,
            randomness: str = 'pseudo'
    ):
        super().__init__(seed, randomness)

        self.mean = mean
        self.std_dev = std_dev

    def sample(self) -> float:
        return self._rng.gauss(self.mean, self.std_dev)


class WaveTableSignalGenerator(PeriodicSignalGenerator):
    def __init__(
            self,
            values: List[float],
            freq: float = None,
            period: float = None,
            clock: Clock = None
    ):
        super().__init__(freq, period, clock)

        self._values = None
        self.set_values(values)

    def get_values(self) -> List[float]:
        return list(self._values)

    def set_values(self, values: List[float]) -> None:
        self._validate_values(values)
        self._values = list(values)

    def _validate_values(self, values: List[float]):
        if not values:
            raise ValueError('values cannot be empty.')

    def sample(self) -> float:
        i = self._get_value_index()
        return self._values[i]

    def _get_value_index(self) -> int:
        i = len(self._values) * self._get_period_fraction()
        return int(i)
