from robotlib.clocks import Clock, RealTimeClock
from robotlib.robot import Robot


class World:
    def __init__(self, sim: bool, clock: Clock):
        self.sim = sim
        self.clock = clock

        self._stop = False

    def run(self, robot: Robot):
        robot.enable(sim=self.sim)

        try:
            while not self._stop:
                try:
                    self.step(robot)
                except KeyboardInterrupt:
                    self.stop()
        finally:
            robot.disable(sim=self.sim)

    def step(self, robot: Robot):
        pass

    def stop(self):
        self._stop = True


class RealWorld(World):
    def __init__(self):
        super().__init__(sim=False, clock=RealTimeClock())
