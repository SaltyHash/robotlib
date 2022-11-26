from typing import NamedTuple, Iterable

import numpy as np


class Color(NamedTuple):
    """A color in the RGB color space. Values should be in the range 0..1."""

    r: float
    g: float
    b: float

    def to_array(self) -> np.ndarray:
        return np.array(self)

    def to_int8(self) -> np.ndarray:
        a = self.to_array()
        a = a * 255
        a = np.round(a)
        a = np.clip(a, 0, 255)
        a = a.astype(np.uint8)
        return a

    def to_hex(self, prefix: str = '0x') -> str:
        r, g, b = self.to_int8()

        color = 0x1000000 | (r << 16) | (g << 8) | b
        color = hex(color)[3:].upper()

        if prefix:
            color = prefix + color

        return color

    @staticmethod
    def from_array(array: np.ndarray) -> 'Color':
        return Color(*array)

    @staticmethod
    def from_int8(r: int, g: int, b: int) -> 'Color':
        return Color(r / 255, g / 255, b / 255)

    @staticmethod
    def from_hex(color: str) -> 'Color':
        if color.startswith('#'):
            color = color[1:]

        color = int(color, 16)

        r = (color & 0xFF0000) >> 16
        g = (color & 0x00FF00) >> 8
        b = (color & 0x0000FF)

        return Color.from_int8(r, g, b)


class Colors:
    BLACK = Color(0., 0., 0.)
    WHITE = Color(1., 1., 1.)
    GRAY = Color(0.5, 0.5, 0.5)

    RED = Color(1., 0., 0.)
    YELLOW = Color(1., 1., 0.)
    GREEN = Color(0., 1., 0.)
    CYAN = Color(0., 1., 1.)
    BLUE = Color(0., 0., 1.)
    MAGENTA = Color(1., 0., 1.)

    @staticmethod
    def get_colors() -> Iterable[Color]:
        return filter(lambda v: isinstance(v, Color), Colors.__dict__.values())
