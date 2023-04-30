import random
import time
from dataclasses import dataclass
from dataclasses import field
from math import pi, atan2

import pygame

from robotlib.geometry import Point2d
from robotlib.kinematics.inverse.solver import InverseSolver
from robotlib.kinematics.forward.solver import ForwardSolver
from robotlib.kinematics.system import System, Length
from robotlib.utils import pick_k
from robotlib.viz.color import Colors
from robotlib.viz.pygame_canvas import PygameCanvas


@dataclass
class RandomInverseSolverStats:
    steps: int = 0
    best_dist: Length = 0.
    stop_reason: str = ''


@dataclass
class RandomInverseSolver(InverseSolver):
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

    stats: 'RandomInverseSolverStats' = field(default_factory=RandomInverseSolverStats)

    should_draw: bool = True

    def solve(
            self,
            system: System,
            target_point: Point2d,
            base_point: Point2d = Point2d(0, 0),
    ) -> System:
        self.stats = RandomInverseSolverStats()

        if self.point_at_target_on_start:
            self._point_arm_at_target(system, target_point, base_point)

        tolerance = self.tolerance ** 2

        self.stats.best_dist = self._get_dist(system, target_point, base_point)
        best_angles = system.angles

        epsilon = self._get_epsilon(self.stats.best_dist, system)

        min_resolution = min(joint.resolution for joint in system.joints)
        min_epsilon = max(self.min_epsilon, min_resolution)

        while True:
            if self.stats.steps > self.max_steps - 1:
                self.stats.stop_reason = 'max steps reached'
                system.angles = best_angles
                break

            if epsilon < min_epsilon:
                self.stats.stop_reason = 'epsilon reached min_epsilon'
                system.angles = best_angles
                break

            dist = self._get_dist(system, target_point, base_point)

            if dist <= tolerance:
                self.stats.best_dist = dist
                self.stats.stop_reason = 'distance within tolerance'
                break

            if dist < self.stats.best_dist:
                self.stats.best_dist = dist
                best_angles = system.angles
                epsilon = self._get_epsilon(dist, system)
            else:
                system.angles = best_angles
                epsilon *= self.epsilon_decay
                self._draw(system, target_point)

            self._jiggle(system, epsilon)

            self._point_end_at_target(system, target_point, base_point)

            self.stats.steps += 1

            # TODO REMOVE THIS
            self._draw(system, target_point, clear=False)

        # TODO REMOVE THIS
        self._draw(system, target_point)

        return system

    def _point_arm_at_target(self, system: System, target_point: Point2d, base_point: Point2d) -> None:
        joints = system.joints
        diff = target_point - base_point
        angle = atan2(diff.y, diff.x)
        joints[0].angle = angle

        for joint in joints[1:]:
            joint.angle = 0

    def _get_dist(self, system: System, target_point: Point2d, base_point: Point2d) -> Length:
        end_point = self.forward_solver.solve(system, base_point=base_point)[-1]

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
        last_joint_position = self.forward_solver.solve(system, base_point=base_point)[-2]

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
            for point in self.forward_solver.solve(system)
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

        time.sleep(1 / 60)
