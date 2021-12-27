"""Provides a representation for your robot's behavior and, optionally, appearance."""
from typing import List, Optional, Any, NamedTuple, Dict

from robotlib.clocks import Clock, RealTimeClock


class Robot:
    def __init__(self, name: str, clock: Clock = None, sim: bool = False):
        self.name = name
        self.clock = clock or RealTimeClock()
        self.sim = sim

        self.body: Optional[RobotBody] = None
        self.devices = []
        self.enable_time_s = None

        self._stop = False

    @property
    def run_time(self) -> float:
        return self.clock.get_time() - self.enable_time_s

    def add_device(self, device: 'Device') -> 'Device':
        self.devices.append(device)
        device.robot = self
        return device

    def enable(self, sim: bool = False):
        for device in self.devices:
            device.enable(sim=sim)

        self.enable_time_s = self.clock.get_time()

    def disable(self, sim: bool = False):
        for device in self.devices:
            device.disable(sim=sim)

    def run(self, world: 'World' = None):
        sim = world is not None
        self.enable(sim=sim)

        try:
            while not self._stop:
                try:
                    self._run_once(world=world)
                except KeyboardInterrupt:
                    self.stop()
        finally:
            self.disable(sim)

    def stop(self):
        self._stop = True

    def process_observation(self, observation: Dict[str, 'InputSample'], start_time_s: float, stop_time_s: float):
        raise NotImplementedError()

    def _run_once(self):
        start_time_s = self.clock.get_time()
        observation = self._make_observation()
        stop_time_s = self.clock.get_time()

        self.process_observation(observation, start_time_s, stop_time_s)

        self._apply_outputs()

    def _make_observation(self) -> Dict[str, 'InputSample']:
        obs = {}

        for device in self.devices:
            for input in device.inputs:
                obs[f'{device.name}.{input.name}'] = input.sample()

        return obs

    def _apply_outputs(self):
        for device in self.devices:
            for output in device.outputs:
                output.apply()


class InputSample(NamedTuple):
    input: 'Input'
    time_s: float
    value: Any


class RobotBody:
    pass


class Device:
    def __init__(self, name: str):
        self.name = name

        self.robot: Optional[Robot] = None
        self.inputs: List['Input'] = []
        self.outputs: List['Output'] = []

    def add_input(self, input: 'Input'):
        self.inputs.append(input)
        input.device = self

    def add_output(self, output: 'Output'):
        self.outputs.append(output)
        output.device = self

    def enable(self, sim: bool):
        pass

    def disable(self, sim: bool):
        pass


class Input:
    def __init__(self, name: str):
        self.name = name

        self.device: Optional[Device] = None

    @property
    def robot(self):
        return self.device.robot if self.device else None

    def sample(self):
        raise NotImplementedError()

    def sample_sim(self, world):
        raise NotImplementedError()


class Output:
    def __init__(self, name: str):
        self.name = name

        self.device: Optional[Device] = None

    @property
    def robot(self):
        return self.device.robot if self.device else None

    def apply(self):
        raise NotImplementedError()

    def apply_sim(self, world):
        raise NotImplementedError()
