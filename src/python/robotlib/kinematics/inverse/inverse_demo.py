import random
import time
from dataclasses import dataclass
from math import pi, cos, sin
from typing import Optional

import numpy as np
import pygame

from robotlib.geometry import Point2d
from robotlib.kinematics.forward.basic_solver import BasicForwardSolver
from robotlib.kinematics.inverse.random_solver import RandomInverseSolver, Context
from robotlib.kinematics.inverse.solver_cache import InverseSolverCache
from robotlib.kinematics.system import System
from robotlib.viz.color import Colors
from robotlib.viz.pygame_canvas import PygameCanvas


class RandomInverseSolverWithDrawing(RandomInverseSolver):
    canvas: PygameCanvas
    should_draw: bool
    fps: Optional[float]

    def __init__(self, *args, should_draw: bool = True, fps: float = 60., **kwargs):
        super().__init__(*args, **kwargs)
        self.should_draw = should_draw
        self.fps = fps

    def start_callback(self, context: 'Context') -> None:
        self._draw(context.system, context.target_point, clear=True)

    def post_step_callback(self, context: 'Context') -> None:
        self._draw(context.system, context.target_point, clear=False)

    def end_callback(self, context: 'Context') -> None:
        self._draw(context.system, context.target_point, clear=True)
        time.sleep(0.5)

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

        if self.fps is not None:
            time.sleep(1 / self.fps)


def test0():
    n = 3
    system = System.from_links(*(1 / n for _ in range(n)))
    # system = System.from_links(1, .75, .56, .42, .32)

    if 0:
        joint = system.joints[0]
        # joint.min_angle = pi / 4
        # joint.max_angle = 3 * pi / 4
        joint.min_angle = 0
        joint.max_angle = pi

    if 0:
        # limit = 2 * pi / len(system.joints)
        limit = pi / 2
        for joint in system.joints[1:]:
            joint.min_angle = -limit
            joint.max_angle = limit

    if 0:
        r = 2 * pi / 360
        for joint in system.joints:
            joint.resolution = r

    solver = RandomInverseSolverWithDrawing(
        BasicForwardSolver(),
        should_draw=True,
        fps=10,
        epsilon_zero=pi,
        epsilon_decay=.8,
        point_at_target_on_start=0,
    )
    solver = InverseSolverCache(solver, precision=0.1)

    angle = 0
    x, dx = .8, .1
    while True:
        max_length = random.random() * system.max_length
        # max_length = system.max_length / 2
        angle = 2 * pi * random.random()
        # angle += 2 * pi / 16
        target_point = Point2d(
            x=max_length * cos(angle),
            y=max_length * sin(angle),
        )

        # if x >= .8 or x <= -.8:
        #     dx *= -1
        # x += dx
        # y = (.8 - abs(x)) * (1 if dx > 0 else -1)
        # target_point = Point2d(x=x, y=y)

        solver.solve(system, target_point)

        print(f'final system: {system}')
        # print(f'len(cache)={len(solver)}')
        # time.sleep(1 / 60)


def test1():
    trials = 20000

    # 1 / (1 - a) = n
    # a = (n - 1) / n

    # rbs = RandomInverseSolver(
    rbs = RandomInverseSolverWithDrawing(
        BasicForwardSolver(),
        # epsilon_zero=pi / 2,
        # epsilon_decay=0.95,
        epsilon_zero=pi,
        epsilon_decay=.96,
        point_at_target_on_start=False,
    )
    bs = InverseSolverCache(rbs, precision=0.1)

    n = 5
    system = System.from_links(*(1 / n for _ in range(n)))

    t_total = StatsTracker()
    steps_total = StatsTracker()
    n_within_tolerance = StatsTracker()

    for _ in range(trials):
        max_length = random.random() * system.max_length
        angle = 2 * pi * random.random()
        target_point = Point2d(
            x=max_length * cos(angle),
            y=max_length * sin(angle),
        )

        t0 = time.monotonic()
        system = bs.solve(system, target_point)
        t1 = time.monotonic()

        t_total.append(t1 - t0)
        steps_total.append(rbs.stats.steps)
        n_within_tolerance.append(1 if rbs.stats.best_dist <= rbs.tolerance else 0)

    print()
    print(f't / trial = {t_total}')
    print(f'steps / trial = {steps_total}')
    print(f'% within tolerance = {n_within_tolerance}')


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


def main():
    test0()


if __name__ == '__main__':
    main()
