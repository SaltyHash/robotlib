"""
Helpful geometry functions.

All functions assume degrees are in Radians unless specified otherwise.
"""

import math
from math import pi
from typing import Tuple


class Point2D:
    __slots__ = (
        'x',
        'y'
    )

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

    def __abs__(self) -> float:
        return math.sqrt(sum(
            value ** 2 for value in self._get_dimensions()
        ))

    def _get_dimensions(self) -> Tuple:
        return self.x, self.y

    def __add__(self, other: 'Point2D') -> 'Point2D':
        return Point2D(
            x=self.x + other.x,
            y=self.y + other.y
        )

    def __eq__(self, other: 'Point2D') -> bool:
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        return f'<x={self.x}, y={self.y}>'


class Point3D(Point2D):
    __slots__ = (
        'z'
    )

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        super().__init__(x=x, y=y)
        self.z = z

    def _get_dimensions(self) -> Tuple:
        return self.x, self.y, self.z

    def __add__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(
            x=self.x + other.x,
            y=self.y + other.y,
            z=self.z + other.z
        )

    def __eq__(self, other: 'Point3D') -> bool:
        return super().__eq__(other) and self.z == other.z

    def __str__(self) -> str:
        return f'<x={self.x}, y={self.y}, z={self.z}>'


def angle_between(start_point: 'Point2D', end_point: 'Point2D') -> float:
    dx = end_point.x - start_point.x
    dy = end_point.y - start_point.y
    return math.atan2(dy, dx)


def angle_between_heading(
        start_point: 'Point2D',
        end_point: 'Point2D',
        heading: float
) -> float:
    angle = angle_between(start_point, end_point)
    angle = angle - heading
    angle = trunc_angle(angle)
    return angle


def trunc_angle(angle: float) -> float:
    """
    Truncates the angle such that it is kept in range ``[-pi, pi)``.

    Examples::

        pi / 2 --> pi / 2
        3 * pi / 2 --> -pi / 2
        5 * pi --> -pi
        1.1 * pi --> -0.9 * pi
    """

    angle += pi
    angle %= 2 * pi
    angle -= pi
    return angle
