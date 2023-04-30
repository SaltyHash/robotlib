from math import cos, sin
from typing import Sequence

from robotlib.geometry import Point2d
from robotlib.kinematics.forward.solver import ForwardSolver
from robotlib.kinematics.system import System


class BasicForwardSolver(ForwardSolver):
    def solve(
            self,
            system: System,
            base_point: Point2d = Point2d(0, 0)
    ) -> Sequence[Point2d]:
        point = base_point
        points = [point]
        angle = 0.

        for joint, link in system.joints_links:
            angle += joint.angle

            point = point + Point2d(
                x=link.length * cos(angle),
                y=link.length * sin(angle),
            )

            points.append(point)

        return points
