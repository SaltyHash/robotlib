import random
from dataclasses import dataclass
from math import pi, atan2

from robotlib.geometry import Point2d
from robotlib.kinematics.forward.solver import ForwardSolver
from robotlib.kinematics.inverse.solver import InverseSolver
from robotlib.kinematics.system import System, Length
from robotlib.utils import pick_k


class RandomInverseSolver(InverseSolver):
    """Uses greedy random search to solve the inverse kinematics of a system."""

    forward_solver: ForwardSolver
    tolerance: float
    max_steps: int
    epsilon_zero: float
    epsilon_decay: float
    epsilon_dist_decay: float
    min_epsilon: float
    point_at_target_on_start: bool
    max_joints_to_jiggle: int
    rng: random.Random

    stats: 'Stats'
    """Info about the last run."""

    def __init__(
            self,
            forward_solver: ForwardSolver,
            tolerance: float = 0.001,
            max_steps: int = 10000,
            epsilon_zero: float = pi / 2,
            epsilon_decay: float = 0.99,
            epsilon_dist_decay: float = .96,
            min_epsilon: float = 0.001,
            point_at_target_on_start: bool = True,
            max_joints_to_jiggle: int = 2,
            rng: random.Random = None,
    ):
        self.forward_solver = forward_solver
        self.tolerance = tolerance
        self.max_steps = max_steps
        self.epsilon_zero = epsilon_zero
        self.epsilon_decay = epsilon_decay
        self.epsilon_dist_decay = epsilon_dist_decay
        self.min_epsilon = min_epsilon
        self.point_at_target_on_start = point_at_target_on_start
        self.max_joints_to_jiggle = max_joints_to_jiggle
        self.rng = rng or random.Random()

    def solve(
            self,
            system: System,
            target_point: Point2d,
            base_point: Point2d = Point2d(0, 0),
    ) -> System:
        self.stats = Stats()

        if self.point_at_target_on_start:
            self._point_arm_at_target(system, target_point, base_point)

        tolerance = self.tolerance ** 2

        self.stats.best_dist = self._get_dist(system, target_point, base_point)
        best_angles = system.angles

        epsilon = self._get_epsilon(self.stats.best_dist, system)

        min_resolution = min(joint.resolution for joint in system.joints)
        min_epsilon = max(self.min_epsilon, min_resolution)

        context = Context(system, target_point, base_point)
        self.start_callback(context)

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

            self._jiggle(system, epsilon)

            self._point_end_at_target(system, target_point, base_point)

            self.stats.steps += 1

            self.post_step_callback(context)

        self.end_callback(context)

        return system

    def start_callback(self, context: 'Context') -> None:
        """Run once before the first step begins."""
        pass

    def post_step_callback(self, context: 'Context') -> None:
        """Run after each step."""
        pass

    def end_callback(self, context: 'Context') -> None:
        """Run after the last step."""
        pass

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


@dataclass
class Stats:
    steps: int = 0
    best_dist: Length = 0.
    stop_reason: str = ''


@dataclass
class Context:
    system: System
    target_point: Point2d
    base_point: Point2d
