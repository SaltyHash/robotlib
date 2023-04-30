from math import floor
from typing import Dict

from robotlib.geometry import Point2d
from robotlib.kinematics.inverse.solver import InverseSolver
from robotlib.kinematics.system import System


class InverseSolverCache(InverseSolver):
    solver: InverseSolver
    precision: float

    _cache: Dict

    def __init__(
            self,
            solver: InverseSolver,
            precision: float,
    ):
        self.solver = solver
        self.precision = precision

        self._cache = {}

    def __len__(self) -> int:
        return self.size

    @property
    def size(self) -> int:
        """The number of entries in the cache. This is also returned by ``len(...)``."""
        return len(self._cache)

    def solve(
            self,
            system: System,
            target_point: Point2d,
            base_point: Point2d = Point2d(0, 0),
    ) -> System:
        system_hash = self._get_system_hash(system)
        target_region = self._quantize(target_point)
        base_region = self._quantize(base_point)
        key = (system_hash, target_region, base_region)

        if key in self._cache:
            system.angles = self._cache[key]

        system = self.solver.solve(system, target_point, base_point)

        if key not in self._cache:
            self._cache[key] = system.angles

        return system

    def _get_system_hash(self, system: System) -> int:
        return hash((
            tuple(link.length for link in system.links),
            tuple(joint.min_angle for joint in system.joints),
            tuple(joint.max_angle for joint in system.joints),
            tuple(joint.resolution for joint in system.joints),
        ))

    def _quantize(self, point: Point2d) -> Point2d:
        return Point2d(
            x=floor(point.x / self.precision),
            y=floor(point.y / self.precision),
        )
