from typing import Optional


class Clipper:
    def __init__(self, min_value: float = None, max_value: float = None):
        self._min_value = None
        self._max_value = None

        self.set_limits(min_value, max_value)

    def set_limits(self, min_value: Optional[float], max_value: Optional[float]) -> None:
        # Clear the max in case it happens to already be set to a value that is
        # lower than the new min_value, which would throw an exception
        self.max_value = None

        self.min_value = min_value
        self.max_value = max_value

    @property
    def min_value(self) -> Optional[float]:
        return self._min_value

    @min_value.setter
    def min_value(self, value: Optional[float]) -> None:
        self._check_min(value)
        self._min_value = value

    def _check_min(self, value: Optional[float]) -> None:
        if value is not None and self._max_value is not None and value > self._max_value:
            raise ValueError(f'Min value ({value}) cannot be greater '
                             f'than max value ({self._max_value}).')

    @property
    def max_value(self) -> Optional[float]:
        return self._max_value

    @max_value.setter
    def max_value(self, value: Optional[float]) -> None:
        self._check_max(value)
        self._max_value = value

    def _check_max(self, value: Optional[float]) -> None:
        if value is not None and self._min_value is not None and value < self._min_value:
            raise ValueError(f'Max value ({value}) cannot be greater '
                             f'than min value ({self._min_value}).')

    def __call__(self, value: float) -> float:
        return self.clip(value)

    def clip(self, value: float) -> float:
        min_value = self.min_value
        if min_value is not None and value <= min_value:
            return min_value

        max_value = self.max_value
        if max_value is not None and value >= max_value:
            return max_value

        return value


class LinearExtrapolator:
    def __init__(
            self,
            x0: float, y0: float, x1: float, y1: float,
            min_output: float = None,
            max_output: float = None
    ):
        self._x0 = x0
        self._y0 = y0

        self._m = (y1 - y0) / (x1 - x0)

        self._clipper = Clipper(min_output, max_output)

    def __call__(self, x: float) -> float:
        return self.extrapolate(x)

    def extrapolate(self, x) -> float:
        value = self._m * (x - self._x0) + self._y0
        value = self._clipper(value)
        return value
