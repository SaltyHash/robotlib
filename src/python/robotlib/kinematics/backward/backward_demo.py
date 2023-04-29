import random
import time
from dataclasses import dataclass
from math import pi, cos, sin

import numpy as np

from robotlib.geometry import Point2d
from robotlib.kinematics.backward.backward_cache import BackwardSolverCache
from robotlib.kinematics.backward.random_backward_solver import RandomBackwardSolver
from robotlib.kinematics.forward import ForwardSolver
from robotlib.kinematics.system import System


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

    bs = RandomBackwardSolver(
        ForwardSolver(),
        epsilon_zero=pi,
        epsilon_decay=.8,
        point_at_target_on_start=0,
    )
    bs = BackwardSolverCache(bs, precision=0.1)

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

        bs.backward(system, target_point)

        print(f'final system: {system}')
        print(f'len(cache)={len(bs)}')
        # time.sleep(1 / 60)


def test1():
    trials = 20000

    # 1 / (1 - a) = n
    # a = (n - 1) / n

    bs = RandomBackwardSolver(
        ForwardSolver(),
        # epsilon_zero=pi / 2,
        # epsilon_decay=0.95,
        epsilon_zero=pi,
        epsilon_decay=.96,

        point_at_target_on_start=False,
        should_draw=False,
    )
    bs = BackwardSolverCache(bs, precision=0.1)

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
        result = bs.backward(system, target_point)
        t1 = time.monotonic()

        t_total.append(t1 - t0)
        steps_total.append(result[1])
        n_within_tolerance.append(1 if result[2] else 0)

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
