from math import cos, sin
from typing import List

from robotlib.geometry import Point2d
from robotlib.kinematics.system import System


class ForwardSolver:
    def forward(
            self,
            system: System,
            base_point: Point2d = Point2d(0, 0)
    ) -> List[Point2d]:
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
