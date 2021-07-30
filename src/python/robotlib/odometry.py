from math import cos, sin
from typing import Dict


class Odometry:
    """Tracks the (x, y) position and angular heading of a robot."""
    def __init__(self, init_pos=(0.0, 0.0), init_heading: float = 0.0) -> None:
        self.x, self.y = init_pos
        self.heading = init_heading

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(x={self.x:.3f}, y={self.y:.3f}, heading={self.heading:.2f})'


class DifferentialOdometry(Odometry):
    """
    Tracks the (x, y) position and angular heading of a robot with differential drive, i.e. two independent drive wheels
    in parallel separated by some distance (the "track width"). Also known as "tank drive" or "skid-steer". This is
    probably the most common form of robot locomotion.
    """

    def __init__(self, track_width: float, init_pos=(0.0, 0.0), init_heading: float = 0.0) -> None:
        super().__init__(init_pos=init_pos, init_heading=init_heading)
        self.track_width = track_width

    def update_from_distance(self, d_l, d_r) -> Dict[str, float]:
        """
        Updates the position (x and y) and heading based on the distance traveled by the wheels.

        :param d_l: Distance traveled by the left wheel [meters].
        :param d_r: Distance traveled by the right wheel [meters].
        :return: A dictionary of the changes.
        """

        return self._update(*differential_odometry_from_distance(d_l, d_r, self.heading, self.track_width))

    def update_from_velocity(self, v_l, v_r, d_t) -> Dict[str, float]:
        """
        Updates the position (x and y) and heading based on the velocity of the wheels over the given period of time.

        :param v_l: Velocity of the left wheel [meters].
        :param v_r: Velocity of the right wheel [meters].
        :param d_t: Duration of time the wheels were rotating at their specified velocities [seconds].
        :return: A dictionary of the changes.
        """

        return self._update(
            *differential_odometry_from_velocity(v_l, v_r, d_t, self.heading, self.track_width),
            d_t=d_t
        )

    def _update(self, d_x: float, d_y: float, d_heading: float, d_t: float = None) -> Dict[str, float]:
        self.x += d_x
        self.y += d_y
        self.heading += d_heading

        return {
            'x': self.x,
            'd_x': d_x,
            'y': self.y,
            'd_y': d_y,
            'heading': self.heading,
            'd_heading': d_heading,
            'd_t': d_t
        }


def differential_odometry_from_velocity(v_l, v_r, d_t, heading, track_width):
    """
    Calculates the change in position and heading of a differential-drive robot given the velocities of its two wheels
    over a given period of time.

    This converts the velocities into distances and calls `differential_odometry_from_distance(...)`.

    :param v_l: Velocity of the left wheel [meters].
    :param v_r: Velocity of the right wheel [meters].
    :param d_t: Duration of time the wheels were rotating at their specified velocities [seconds].
    :param heading: Initial heading of the robot before travel [radians].
    :param track_width: Distance between the wheels [meters].
    :return: Tuple (d_x, d_y, d_heading), where d_x and d_y represent the change in the X- and Y-dimensions [meters],
        respectively, and d_heading represents the change in the heading [radians].
    """

    d_l = v_l * d_t
    d_r = v_r * d_t
    return differential_odometry_from_distance(d_l, d_r, heading, track_width)


def differential_odometry_from_distance(d_l, d_r, heading, track_width):
    """
    Calculates the change in position and heading of a differential-drive robot given the distance traveled by its two
    drive wheels.

    The equations used in this function were derived from the following PDF...
        http://www.cs.columbia.edu/~allen/F17/NOTES/icckinematics.pdf
    ... which was itself derived from Dudek and Jenkin's Computational Principles of Mobile Robotics.

    :param d_l: Distance traveled by the left wheel [meters].
    :param d_r: Distance traveled by the right wheel [meters].
    :param heading: Initial heading of the robot before travel [radians].
    :param track_width: Distance between the wheels [meters].
    :return: Tuple (d_x, d_y, d_heading), where d_x and d_y represent the change in the X- and Y-dimensions [meters],
        respectively, and d_heading represents the change in the heading [radians].
    """

    # These equations bear little direct resemblance to those shown in the PDF linked to above; they have been reduced
    # in order to minimize the amount of unnecessary computation, and modified to use distances instead of velocities.

    # TODO: Use numpy if arrays are passed in so a massive number of these calculations can be performed in parallel

    if d_l == d_r:
        d_x = cos(heading) * d_l
        d_y = sin(heading) * d_l
        d_heading = 0.0
    else:
        d_heading = (d_r - d_l) / track_width
        R = (track_width / 2) * (d_r + d_l) / (d_r - d_l)

        a = cos(d_heading) - 1
        b = sin(d_heading)
        c = R * sin(heading)
        d = -R * cos(heading)

        d_x = a * c - b * d
        d_y = b * c + a * d

    return d_x, d_y, d_heading
