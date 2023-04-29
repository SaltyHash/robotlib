from robotlib.geometry import Point2d
from robotlib.kinematics.system import System


class BackwardSolver:
    def backward(
            self,
            system: System,
            end_point: Point2d,
            base_point: Point2d = Point2d(0, 0)
    ) -> System:
        ...
