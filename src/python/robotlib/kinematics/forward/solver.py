from typing import Sequence

from robotlib.geometry import Point2d
from robotlib.kinematics.system import System


class ForwardSolver:
    def solve(
            self,
            system: System,
            base_point: Point2d = Point2d(0, 0)
    ) -> Sequence[Point2d]:
        ...
