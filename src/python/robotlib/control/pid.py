from robotlib.mathutils import Clipper


class PID:
    def __init__(
            self,
            p: float, i: float, d: float,
            output_gain: float = 1.0,
            min_output: float = None,
            max_output: float = None
    ):
        self.p = p
        self.i = i
        self.d = d
        self.output_gain = output_gain

        self.target = None
        self.input = None

        self._error_sum = 0.0
        self._prev_error = 0.0

        self._output_clipper = Clipper(min_output, max_output)

    def set_target(self, value: float) -> None:
        self.target = value

    def set_input(self, value: float) -> None:
        self.input = value

    def get_output(self, dt: float) -> float:
        error = self.get_error()

        p = self._get_p_error(error)
        i = self._get_i_error(error, dt)
        d = self._get_d_error(error, dt)

        output = self.output_gain * (p + i + d)
        output = self._output_clipper(output)

        return output

    def get_error(self) -> float:
        return self.target - self.input

    def _get_p_error(self, error) -> float:
        return self.p * error

    def _get_i_error(self, error: float, dt: float) -> float:
        self._error_sum += error * dt

        i_error = self.i * self._error_sum

        return i_error

    def _get_d_error(self, error: float, dt: float) -> float:
        prev_error = self._prev_error
        self._prev_error = error

        if self.d == 0:
            return 0

        d_error = (error - prev_error) / dt
        d_error = self.d * d_error

        self._prev_error = error

        return d_error
