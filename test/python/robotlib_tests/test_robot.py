from typing import Dict
from unittest import TestCase
from robotlib.robot import Robot, InputSample, Input, Device, Output


class TestRobot(TestCase):
    def test_enable(self):
        self.fail()

    def test_disable(self):
        self.fail()


class UltrasonicInput(Input):
    def sample(self):
        import random
        return 100 * random.random()

    def sample_sim(self, world):
        return self.sample()


class DriveMotorOutput(Output):
    def apply(self):
        # TODO
        pass

    def apply_sim(self, world):
        # TODO
        world.set_robot_linear_velocity(self.device.linear_velocity)
        world.set_robot_angular_velocity(self.device.angular_velocity)


class DriveMotors(Device):
    def __init__(self, name: str):
        super().__init__(name)

        self.linear_velocity = 0
        self.angular_velocity = 0

        self.add_output(DriveMotorOutput('velocity'))


class BasicRobot(Robot):
    def __init__(self, name: str):
        super().__init__(name)

        ultrasonic_sensor = Device('ultrasonic_sensor')
        ultrasonic_sensor.add_input(UltrasonicInput('distance'))
        self.add_device(ultrasonic_sensor)

        self.drive_motors: DriveMotors = self.add_device(DriveMotors('drive_motors'))

    def process_observation(self, observation: Dict[str, InputSample], start_time_s: float, stop_time_s: float):
        print(observation)
        print(start_time_s)
        print(stop_time_s)

        if self.run_time >= 0.001:
            self.stop()


class TestBasicRobot(TestCase):
    def setUp(self) -> None:
        self.robot = BasicRobot('My Robot')

    def test_run(self):
        self.robot.run()
