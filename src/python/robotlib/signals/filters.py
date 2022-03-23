from math import pi


class _SimpleFilter:
    def __init__(self, cutoff_freq: float, init_value: float = 0.0):
        self._cutoff_freq = None
        self.set_cutoff_freq(cutoff_freq)

        self._prev_output = init_value

    def get_cutoff_freq(self) -> float:
        return self._cutoff_freq

    def set_cutoff_freq(self, cutoff_freq: float) -> None:
        self._check_cutoff_freq(cutoff_freq)
        self._cutoff_freq = cutoff_freq

    def _check_cutoff_freq(self, cutoff_freq: float) -> None:
        if cutoff_freq < 0:
            raise ValueError(f'cutoff_freq must be >= 0; got {cutoff_freq}.')

    def filter(self, value: float, dt: float) -> float:
        output = self._filter(value, dt)
        self._prev_output = output
        return output

    def _filter(self, value: float, dt: float) -> float:
        raise NotImplementedError()


class LowPassFilter(_SimpleFilter):
    """
    Passes signals lower than the cutoff frequency. Decreases signals higher
    than the cutoff frequency. The higher a signal's frequency is above the
    cutoff frequency, the more the signal is decreased.

    This is also known as a "moving average".

    This is useful for example if you have a sensor reading that is really
    "noisy" (perhaps an accelerometer or distance sensor), and you want to get a
    sort of averaged, slower-moving reading from the noisy readings.

    https://en.wikipedia.org/wiki/Low-pass_filter
    """

    def _filter(self, value: float, dt: float) -> float:
        alpha = self._get_alpha(dt)
        return alpha * value + (1 - alpha) * self._prev_output

    def _get_alpha(self, dt: float) -> float:
        cutoff_freq = self.get_cutoff_freq()
        a = 2 * pi * dt * cutoff_freq
        return a / (a + 1)


class HighPassFilter(_SimpleFilter):
    """
    Passes signals higher than the cutoff frequency. Decreases signals lower
    than the cutoff frequency. The lower a signal's frequency is below the
    cutoff frequency, the more the signal is decreased.

    This is useful for example if you have a sensor reading that has a slowly
    changing bias, for example a gyroscope. This can remove the bias from the
    rapidly varying true signal.

    https://en.wikipedia.org/wiki/High-pass_filter
    """

    def __init__(self, cutoff_freq: float, init_value: float = 0.0):
        super().__init__(cutoff_freq, init_value)
        self._prev_value = init_value

    def _filter(self, value: float, dt: float) -> float:
        d_value = value - self._prev_value
        self._prev_value = value

        alpha = self._get_alpha(dt)
        return alpha * (self._prev_output + d_value)

    def _get_alpha(self, dt: float) -> float:
        cutoff_freq = self.get_cutoff_freq()
        return 1 / (2 * pi * dt * cutoff_freq + 1)
