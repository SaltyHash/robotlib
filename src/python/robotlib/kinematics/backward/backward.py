import random
from dataclasses import dataclass
from dataclasses import field
from itertools import count
from math import pi, atan2, floor
from typing import Dict

import numpy as np
import pygame

from robotlib.geometry import Point2d
from robotlib.kinematics.forward import ForwardSolver
from robotlib.kinematics.system import System, Length
from robotlib.utils import pick_k
from robotlib.viz.color import Colors
from robotlib.viz.pygame_canvas import PygameCanvas


class BackwardSolver:
    def backward(
            self,
            system: System,
            end_point: Point2d,
            base_point: Point2d = Point2d(0, 0)
    ) -> System:
        ...


@dataclass
class RandomBackwardSolverStats:
    steps: int = 0
    final_dist: Length = 0.
    stop_reason: str = ''


@dataclass
class RandomBackwardSolver(BackwardSolver):
    forward_solver: ForwardSolver
    tolerance: float = 0.001
    max_steps: int = 10000
    epsilon_zero: float = pi / 2
    epsilon_decay: float = 0.99
    epsilon_dist_decay: float = .96
    min_epsilon: float = 0.001
    point_at_target_on_start: bool = True
    max_joints_to_jiggle: int = 2
    rng: random.Random = field(default_factory=random.Random)

    stats: 'RandomBackwardSolverStats' = field(default_factory=RandomBackwardSolverStats)

    should_draw: bool = True

    def backward(
            self,
            system: System,
            target_point: Point2d,
            base_point: Point2d = Point2d(0, 0),
    ) -> System:
        self.stats = RandomBackwardSolverStats()

        if self.point_at_target_on_start:
            self._point_arm_at_target(system, target_point, base_point)

        tolerance = self.tolerance ** 2

        best_dist = self._get_dist(system, target_point, base_point)
        best_angles = system.angles

        epsilon = self._get_epsilon(best_dist, system)

        min_resolution = min(joint.resolution for joint in system.joints)
        min_epsilon = max(self.min_epsilon, min_resolution)

        for step in count():
            if step + 1 >= self.max_steps:
                system.angles = best_angles
                print(f'[{step}] Max steps reached: {self.max_steps}')
                break

            if epsilon < min_epsilon:
                system.angles = best_angles
                print(f'[{step}] epsilon reached min_epsilon: {min_epsilon}')
                break

            dist = self._get_dist(system, target_point, base_point)

            if dist <= tolerance:
                print(f'[{step}] final dist: {dist ** 0.5}')
                best_dist = dist
                break

            if dist < best_dist:
                best_dist = dist
                best_angles = system.angles
                epsilon = self._get_epsilon(dist, system)
            else:
                system.angles = best_angles
                epsilon *= self.epsilon_decay
                self._draw(system, target_point)

            self._jiggle(system, epsilon)

            self._point_end_at_target(system, target_point, base_point)

            self._draw(system, target_point, clear=False)

        print(f'best dist: {best_dist ** 0.5}')
        self._draw(system, target_point)

        return system, step + 1, best_dist <= tolerance

    def _point_arm_at_target(self, system: System, target_point: Point2d, base_point: Point2d) -> None:
        joints = system.joints
        diff = target_point - base_point
        angle = atan2(diff.y, diff.x)
        joints[0].angle = angle

        for joint in joints[1:]:
            joint.angle = 0

    def _get_dist(self, system: System, target_point: Point2d, base_point: Point2d) -> Length:
        end_point = self.forward_solver.forward(system, base_point=base_point)[-1]

        dist = target_point - end_point
        dist = dist.x ** 2 + dist.y ** 2
        return dist

    def _get_epsilon(self, best_dist: Length, system: System) -> float:
        return self.epsilon_zero * (
                self.epsilon_dist_decay * best_dist / (2 * system.max_length)
                + (1 - self.epsilon_dist_decay)
        )

    def _jiggle(self, system: System, epsilon: float) -> None:
        joints = system.joints[:-1]

        if 0 <= self.max_joints_to_jiggle < len(joints):
            joints = pick_k(joints, k=self.max_joints_to_jiggle, rng=self.rng)

        for joint in joints:
            joint.angle += epsilon * self.rng.uniform(-1, 1)

    def _point_end_at_target(self, system: System, target_point: Point2d, base_point: Point2d) -> None:
        last_joint = system.joints[-1]
        last_joint_position = self.forward_solver.forward(system, base_point=base_point)[-2]

        angle_to_target = atan2(
            target_point.y - last_joint_position.y,
            target_point.x - last_joint_position.x,
        )

        global_joint_angle = sum(j.angle for j in system.joints)
        last_joint.angle -= global_joint_angle - angle_to_target

    def _draw(self, system: System, target: Point2d, clear: bool = True) -> None:
        if not self.should_draw:
            return

        try:
            canvas = self.canvas
        except AttributeError:
            pygame.init()
            surface = pygame.display.set_mode((800, 800))
            canvas = self.canvas = PygameCanvas(surface)

        scale = canvas.height / 2 / system.max_length
        base_point = canvas.center

        points = [
            scale * point + base_point
            for point in self.forward_solver.forward(system)
        ]

        if clear:
            canvas.fill(Colors.WHITE)

        canvas.draw_circle(base_point, scale * system.max_length, width=1)

        for i in range(len(points) - 1):
            point_a, point_b = points[i:i + 2]
            canvas.draw_line(point_a, point_b, Colors.BLACK, width=1)

        for point in points:
            canvas.draw_circle(point, 3, Colors.GRAY)

        target_radius = round(scale * self.tolerance)
        target_radius = max(target_radius, 3)
        canvas.draw_circle(scale * target + base_point, target_radius, Colors.GREEN)

        canvas.render()
        pygame.event.clear()

        # time.sleep(1 / 60)


class BackwardSolverCache(BackwardSolver):
    solver: BackwardSolver
    precision: float

    _cache: Dict

    def __init__(
            self,
            solver: BackwardSolver,
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

    def backward(
            self,
            system: System,
            target_point: Point2d,
            base_point: Point2d = Point2d(0, 0),
    ) -> System:
        # TODO Some more unique hash of the system
        system_hash = tuple(link.length for link in system.links)
        target_region = self._quantize(target_point)
        base_region = self._quantize(base_point)
        key = (system_hash, target_region, base_region)

        if key in self._cache:
            system.angles = self._cache[key]

        system, *other = self.solver.backward(system, target_point, base_point)

        if key not in self._cache:
            self._cache[key] = system.angles

        return system, *other

    def _quantize(self, point: Point2d) -> Point2d:
        return Point2d(
            x=floor(point.x / self.precision),
            y=floor(point.y / self.precision),
        )


class StatsTracker(list):
    def __str__(self) -> str:
        stats = self.get_stats()
        std_percent = 100. * stats.std / abs(stats.mean)
        return f'{stats.mean:.4} ± {stats.std:.4} ({std_percent:.4}%) [{stats.min:.4}, {stats.max:.4}]'

    def get_stats(self):
        data = np.array(self, dtype=float)
        return Stats(data.mean(), data.std(), data.min(), data.max())


@dataclass
class Stats:
    mean: float
    std: float
    min: float
    max: float
