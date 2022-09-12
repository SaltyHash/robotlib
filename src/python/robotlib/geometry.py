"""
Helpful geometry functions.

All functions assume degrees are in Radians unless specified otherwise.
"""

import math
from math import pi
from numbers import Real
from typing import NamedTuple


class Vector2d(NamedTuple):
    x: Real
    y: Real

    def __str__(self) -> str:
        return f'<x={self.x}, y={self.y}>'

    def __abs__(self) -> 'Vector2d':
        return Vector2d(abs(self.x), abs(self.y))

    def __add__(self, other) -> 'Vector2d':
        other = self._to_vector2d(other)
        return Vector2d(self.x + other.x, self.y + other.y)

    def __radd__(self, other) -> 'Vector2d':
        return self.__add__(other)

    def __sub__(self, other) -> 'Vector2d':
        other = self._to_vector2d(other)
        return Vector2d(self.x - other.x, self.y - other.y)

    def __rsub__(self, other) -> 'Vector2d':
        other = self._to_vector2d(other)
        return Vector2d(other.x - self.x, other.y - self.y)

    def __mul__(self, other) -> 'Vector2d':
        other = self._to_vector2d(other)
        return Vector2d(self.x * other.x, self.y * other.y)

    def __rmul__(self, other) -> 'Vector2d':
        return self.__mul__(other)

    def __truediv__(self, other) -> 'Vector2d':
        other = self._to_vector2d(other)
        return Vector2d(self.x / other.x, self.y / other.y)

    def __rtruediv__(self, other) -> 'Vector2d':
        other = self._to_vector2d(other)
        return Vector2d(other.x / self.x, other.y / self.y)

    def __floordiv__(self, other) -> 'Vector2d':
        other = self._to_vector2d(other)
        return Vector2d(self.x // other.x, self.y // other.y)

    def __rfloordiv__(self, other) -> 'Vector2d':
        other = self._to_vector2d(other)
        return Vector2d(other.x // self.x, other.y // self.y)

    def copy(self, x: Real = None, y: Real = None) -> 'Vector2d':
        return Vector2d(
            x=self.x if x is None else x,
            y=self.y if y is None else y
        )

    def _to_vector2d(self, other) -> 'Vector2d':
        if isinstance(other, Vector2d):
            return other
        elif isinstance(other, Real):
            return Vector2d(other, other)
        else:
            return Vector2d(other[0], other[1])


class Point3D:
    __slots__ = (
        'x',
        'y',
        'z'
    )

    def __init__(self, x: Real, y: Real, z: Real):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return f'<x={self.x}, y={self.y}, z={self.z}>'

    # TODO: Add math operations as in Point2d


def angle_between(start_point: 'Vector2d', end_point: 'Vector2d') -> float:
    """
    Returns the angle in Radians from the start point to the end point,
    in the range (-pi, pi].
    """

    dx = end_point.x - start_point.x
    dy = end_point.y - start_point.y
    return math.atan2(dy, dx)


def angle_between_heading(
        start_point: 'Vector2d',
        end_point: 'Vector2d',
        heading: float
) -> float:
    """
    Returns the angle between the heading at the start point to the end point.

    This is useful if you have a robot with a particular heading located at the
    start point, and you want to determine the angle of the robot's heading to
    some end point for navigation purposes.

    :param start_point:
    :param end_point:
    :param heading: Relative to start_point. In Radians.
    :return: Angle (Radians) in range (-pi, pi].
    """

    angle = angle_between(start_point, end_point)
    angle = angle - heading
    angle = trunc_angle(angle)
    return angle


def trunc_angle(angle: float) -> float:
    """
    Truncates the angle such that it is kept in range ``(-pi, pi]``.

    Examples::

        0      --> 0
        pi     --> pi
        -pi    --> pi
        pi/2   --> pi/2
        3 pi/2 --> -pi/2
        5 pi   --> pi
        1.1 pi --> -0.9 pi
    """

    # Shift the angle up
    angle += pi

    # Truncate the angle to range (0, 2 * pi]
    #     mod( x, y) --> [ 0, y)
    #     mod(-x, y) --> ( y, 0]
    #   - mod(-x, y) --> (-y, 0]
    # y - mod(-x, y) --> (0, y]
    two_pi = 2 * pi
    angle = two_pi - (-angle % two_pi)

    # Shift the angle back down
    angle -= pi

    return angle
