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
    """
    Returns the angle in Radians from the start point to the end point,
    in the range (-pi, pi].
    """

    dx = end_point.x - start_point.x
    dy = end_point.y - start_point.y
    return math.atan2(dy, dx)


def angle_between_heading(
        start_point: 'Point2D',
        end_point: 'Point2D',
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
