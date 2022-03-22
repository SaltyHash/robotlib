from math import pi


class LowPassFilter:
    """
    https://en.wikipedia.org/wiki/Low-pass_filter
    """

    def __init__(self, cutoff_freq: float, init_value: float = 0.0):
        self._cutoff_freq = None
        self.set_cutoff_freq(cutoff_freq)

        self._prev_output = init_value

    def get_cutoff_freq(self) -> float:
        return self._cutoff_freq

    def set_cutoff_freq(self, cutoff_freq: float) -> None:
        if cutoff_freq < 0:
            raise ValueError(f'cutoff_freq must be >= 0; got {cutoff_freq}.')

        self._cutoff_freq = cutoff_freq

    def filter(self, value: float, dt: float) -> float:
        output = self._filter(value, dt)
        self._prev_output = output
        return output

    def _filter(self, value: float, dt: float) -> float:
        alpha = self._get_alpha(dt)
        return alpha * value + (1 - alpha) * self._prev_output

    def _get_alpha(self, dt: float) -> float:
        cutoff_freq = self.get_cutoff_freq()
        a = 2 * pi * dt * cutoff_freq
        return a / (a + 1)
