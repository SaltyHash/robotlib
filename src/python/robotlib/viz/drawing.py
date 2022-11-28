from abc import ABC, abstractmethod
from enum import Enum
from numbers import Real
from typing import Union, NamedTuple, Optional

from robotlib.geometry import Vector2d, Point2d
from robotlib.viz.color import Color, Colors

FILLED = 'filled'

Width = Union[int, float, FILLED]


class Size2d(NamedTuple):
    width: Real
    height: Real


Position2d = Vector2d


class Canvas(ABC):
    """
    A 2D surface that can be drawn on.

    Point (0, 0) corresponds to the bottom-left of the canvas.
    Point (width, height) corresponds to the top-right of the canvas.
    """

    @property
    def size(self) -> Size2d:
        return self.get_size()

    @property
    def width(self) -> Real:
        return self.size.width

    @property
    def height(self) -> Real:
        return self.size.height

    @property
    def center(self) -> Point2d:
        size = self.size
        return Point2d(size.width // 2, size.height // 2)

    @property
    def left_bottom(self) -> Point2d:
        return Point2d(0, 0)

    @property
    def right_bottom(self) -> Point2d:
        return Point2d(self.width, 0)

    @property
    def left_top(self) -> Point2d:
        return Point2d(0, self.height)

    @property
    def right_top(self) -> Point2d:
        size = self.size
        return Point2d(size.width, size.height)

    @abstractmethod
    def get_size(self) -> Size2d:
        ...

    @abstractmethod
    def draw_line(self, p1, p2, color: Color = Colors.BLACK, width: Width = 1.0):
        ...

    @abstractmethod
    def draw_circle(self, center, radius, color: Color = Colors.BLACK, width: Width = FILLED):
        ...

    @abstractmethod
    def draw_rect(self, left_bottom, width_height, color: Color = Colors.BLACK, width: Width = FILLED):
        ...

    def draw_square(self, left_bottom, size, color: Color = Colors.BLACK, width: Width = FILLED):
        self.draw_rect(left_bottom, (size, size), color=color, width=width)

    @abstractmethod
    def draw_text(
            self,
            message: str,
            left_bottom,
            color: Color = Colors.BLACK,
            font_size: int = 12
    ) -> Optional[Size2d]:
        ...

    def fill(self, color: Color):
        self.draw_rect(
            left_bottom=self.left_bottom,
            width_height=self.size,
            color=color,
            width=FILLED
        )

    @abstractmethod
    def render(self):
        ...


class Drawable(ABC):
    def is_visible(self, camera):
        return True

    @abstractmethod
    def draw(self, canvas: Canvas):
        ...


class Corner(Enum):
    LEFT_BOTTOM = (0, 0)
    RIGHT_BOTTOM = (1, 0)
    LEFT_TOP = (0, 1)
    RIGHT_TOP = (1, 1)
