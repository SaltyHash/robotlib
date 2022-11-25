import itertools
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import inf
from typing import Tuple, Any, Callable, Iterable, Optional, TypeVar

T = TypeVar('T')


def count(start: int = 0, step: int = 1, stop: int = None) -> Iterable[int]:
    """
    Yields values from ``start`` to ``stop`` (not included), separated by ``steps``.

    If ``stop`` is not specified, then this yields values forever.

    This is essentially the ``itertools.count`` function, but with the addition of the stop functionality.
    """

    if stop is None:
        stop = inf

    for i in itertools.count(start, step):
        if i < stop:
            yield i
        else:
            return


def or_default(item: Optional[Any], default: Optional[Any]) -> Optional[Any]:
    return default if item is None else item


def minmax(*items: T, default: Any = None, key: Callable[[T], Any] = None) -> tuple[T, T]:
    """
    Like the ``min()`` and ``max()`` functions, but returns a tuple of both the minimum and maximum values while only
    iterating over the items once.
    """

    if len(items) == 0:
        raise TypeError('minmax expected at least 1 argument, got 0')
    elif len(items) == 1:
        iterator = iter(items[0])
    else:
        iterator = iter(items)

    try:
        most_min = most_max = next(iterator)
    except StopIteration:
        if default is not None:
            return default
        else:
            raise ValueError('minmax() arg is an empty sequence')

    for item in iterator:
        most_min = min(most_min, item, key=key)
        most_max = max(most_max, item, key=key)

    return most_min, most_max


def setup_basic_logging(
        *args,
        format: str = "[%(asctime)s %(levelname)s %(name)s] %(message)s",
        level=logging.INFO,
        **kwargs
) -> None:
    logging.basicConfig(*args, format=format, level=level, **kwargs)


class DictWithDefault(dict):
    """A dict that returns a default value for missing keys."""

    def __init__(self, default: Any, **kwargs):
        super().__init__(**kwargs)
        self.default = default

    def __getitem__(self, item: Any) -> Any:
        return self.get(item, self.default)


@dataclass
class PrioritizedItem:
    """For use with ``queue.PriorityQueue`` when the item is not directly comparable."""

    priority: float
    item: Any

    def __lt__(self, other: 'PrioritizedItem') -> bool:
        return self.priority < other.priority


class RunLimit(ABC):
    def __bool__(self) -> bool:
        return self.keep_running()

    @abstractmethod
    def keep_running(self) -> bool:
        ...


class RuntimeLimit(RunLimit):
    def __init__(self, limit: float, clock: Callable[[], float] = time.monotonic):
        self.limit = limit
        self.clock = clock
        self.t_start = None

    @property
    def _now(self) -> float:
        return self.clock()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def start(self) -> None:
        if self.t_start is not None:
            raise RuntimeError('RuntimeLimit has already been started')

        self.t_start = self._now

    def keep_running(self) -> bool:
        elapsed_time = self._now - self.t_start
        return elapsed_time < self.limit


class Timer:
    def __init__(
            self,
            wall_clock: Callable[[], float] = time.monotonic,
            cpu_clock: Callable[[], float] = time.process_time,
    ):
        self.wall_clock = wall_clock
        self.cpu_clock = cpu_clock

        self._start_t_wall = 0.
        self._start_t_cpu = 0.
        self.reset()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __str__(self) -> str:
        t_wall, t_cpu = self.sample
        return f'wall_time={t_wall}; cpu_time={t_cpu}'

    def reset(self) -> None:
        self._start_t_wall, self._start_t_cpu = self.wall_clock(), self.cpu_clock()

    @property
    def sample(self) -> Tuple[float, float]:
        stop_t_wall, stop_t_cpu = self.wall_clock(), self.cpu_clock()
        return stop_t_wall - self._start_t_wall, stop_t_cpu - self._start_t_cpu
