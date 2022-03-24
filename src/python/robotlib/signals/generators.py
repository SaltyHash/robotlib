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
    def __init__(self, freq: float):
        self._freq = freq

        self._t = 0.0

    def get_freq(self) -> float:
        return self._freq

    def set_freq(self, freq: float) -> None:
        self._validate_freq(freq)
        self._freq = freq

    def _validate_freq(self, freq: float) -> None:
        if freq < 0:
            raise ValueError(f'freq must be >= 0; got {freq}.')


class SineWaveGenerator(PeriodicSignalGenerator):
    def sample(self, dt: float) -> float:
        self._t += dt
        sample = math.sin(2 * pi * self._freq * self._t)
        return sample
