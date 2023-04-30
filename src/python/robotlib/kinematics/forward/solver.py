from abc import abstractmethod
from typing import Sequence

from robotlib.geometry import Point2d
from robotlib.kinematics.system import System


class ForwardSolver:
    @abstractmethod
    def solve(
            self,
            system: System,
            base_point: Point2d = Point2d(0, 0)
    ) -> Sequence[Point2d]:
        """
        Solve the forward kinematics of the system, returning a sequence of link
        end points. The first point in the sequence is the base point, and the last
        point in the sequence is the end effector point.
        """

        ...
