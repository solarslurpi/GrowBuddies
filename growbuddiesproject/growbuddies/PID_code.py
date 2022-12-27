import time
import warnings
from enum import Enum
from growbuddies.settings_code import Settings
from growbuddies.logginghandler import LoggingHandler

try:
    # Get monotonic time to ensure that time deltas are always positive
    _current_time = time.monotonic
except AttributeError:
    # time.monotonic() not available (using python < 3.3), fallback to time.time()
    _current_time = time.time
    warnings.warn("time.monotonic() not available in python < 3.3, using time.time() as fallback")


def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    elif (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value


class growthStage(Enum):
    """An enumeration to let growBuddy know if the plants it is caring for are in the vegetative or flower growth stage.

    :param Enum: This setting can be either 'VEG' for the vegetative stage or 'FLOWER' for the flowering stage of the plant.

    """

    VEG = 2
    FLOWER = 3


class PID(object):
    """A simple PID controller."""

    def __init__(self):
        """
        Initialize a new PID controller.

        :param Kp: The value for the proportional gain Kp.
        :param Ki: The value for the integral gain Ki.
        :param Kd: The value for the derivative gain Kd.
        :param setpoint: The setpoint is the target value that the PID controller will attempt to achieve.
        :param sample_time: **MistBuddy does not use the sample time.** The sampling time for the PID controller
            is determined by the frequency of SnifferBuddy MQTT messages.
        :param output_limits: Output limits can be specified as an iterable with two elements, such as (lower, upper).
            These limits ensure that the output will never exceed the upper limit or fall below the lower limit. Either
            limit can be set to None if there is no limit in that direction.
        :param auto_mode: **not used by MistBuddy** Whether the controller should be enabled (auto mode) or not (manual mode)
        :param proportional_on_measurement: **not used by MistBuddy** Whether the proportional term should be calculated on
            the input directly rather than on the error (which is the traditional way). Using
            proportional-on-measurement avoids overshoot for some types of systems.
        :param error_map: **not used by MistBuddy** Function to transform the error value in another constrained value.
        """
        self.logger = LoggingHandler()
        settings = Settings()
        settings.load()
        # Extract the logging level
        pid_settings = settings.get("PID_settings")
        # Start out with these as the base values.  They will be increased if the error tolerance is too much.
        self.Kp = pid_settings["Kp"]
        self.Ki = pid_settings["Ki"]
        self.Kd = pid_settings["Kd"]
        self.tolerance = pid_settings["tolerance"]
        # Set up the setpoint to the ideal vpd value.
        self.setpoint = 0.0
        vpd_setpoint_settings = settings.get("vpd_setpoints")
        vpd_growth_stage = settings.get("vpd_growth_stage")
        # String to enum - match on the name attribute.
        if vpd_growth_stage.upper() == growthStage.VEG.name:
            self.setpoint = vpd_setpoint_settings["veg"]
        else:
            self.setpoint = vpd_setpoint_settings["flower"]
        if not isinstance(self.setpoint, float) or self.setpoint * 10 not in range(20):
            raise Exception("The vpd setpoint should be a floating point number between 0.0 and less than 2.0")
        self.output_limits_min = pid_settings["output_limits"][0]
        self.output_limits_max = pid_settings["output_limits"][1]
        self.integral_limits_min = pid_settings["integral_limits"][0]
        self.integral_limits_max = pid_settings["integral_limits"][1]

        self._min_output, self._max_output = None, None
        pid_settings = settings.get("PID_settings")

        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._prev_error = None

        self._count = 0
        self._sum = 0

        self._last_time = _current_time()
        self._last_output = None
        self._last_input = None

        self.ideal_setting = False

        self.output_limits = pid_settings["output_limits"][0], pid_settings["output_limits"][1]

    def __call__(self, input_, dt=None):
        """
        Update the PID controller.

        Call the PID controller with *input_* and calculate and return a control output if
        sample_time seconds has passed since the last update. If no new output is calculated,
        return the previous output instead (or None if no value has been calculated yet).

        :param dt: If set, uses this value for timestep instead of real time. This can be used in
            simulations when simulation time is different from real time.
        """

        now = _current_time()
        if dt is None:
            dt = now - self._last_time if (now - self._last_time) else 1e-16
        elif dt <= 0:
            raise ValueError("dt has negative value {}, must be positive".format(dt))
        self.logger.debug(f"--> In the PID CONTROLLER.  {dt} seconds have elapsed since the last reading.")
        self._last_time = now
        # Compute error terms - Note: When the error is positive, the humidity is too low.  There is no dehumidifier.
        # However, we'll keep note of the error in the derivative and integral terms since these accumulate.
        error = self.setpoint - input_
        d_input = input_ - (self._last_input if (self._last_input is not None) else input_)
        self._compute_terms(d_input, error, dt)
        self.logger.debug(
            f"error: {error:.2f}, P: {self._proportional:.2f}, I: {self._integral:.2f}, D: {self._derivative:.2f}"
        )
        # It is getting too humid.  Since we only have a humidifier to adjust, we return.
        if error > self.tolerance:
            self.ideal_setting = True
            return 0, 0
        # Do a bit of autotuning until it grows to big.  Cap it when the air gets too moist.
        if error < self.tolerance and not self.ideal_setting:
            self.Kp += 1
            # self.Ki += 0.05
            # self.Kd += 0.01
            self.logger.debug(f"***>updating coefficients Kp {self.Kp} Ki {self.Ki}  Kd {self.Kd}")
        else:
            self.logger.debug(f"***>NOT updating coefficients ")

        # Compute number of seconds to turn on mistBuddy, which is 0 or a positive number of seconds.

        output = abs(self._proportional + self._integral + self._derivative)
        nSecondsOn = int(round(output))
        nSecondsOn = _clamp(nSecondsOn, self.output_limits)
        self.logger.debug(f" nSecondsOn is {nSecondsOn}")

        # Keep track of state
        self._last_output = output
        self._last_input = input_
        self._prev_error = error
        return nSecondsOn, error

    def _compute_terms(self, d_input, error, dt):
        # Compute integral and derivative terms
        # Since we are not using PID during the night, we reset the error terms and start over.
        self._proportional = self.Kp * error
        # Accomodate maintaining steady state...
        if error == 0:
            self._proportional = self.Kp * -0.1

        self._integral += self.Ki * error * dt
        # I can see how the integral value forces the steady state the Kp gain brought closer to the setpoint.
        # However, the Ki terms seems to grow to a devastatingly large number which causes oscillation.  From
        # watching the vpd values, I'm clamping the contribution to a maximum of 2 seconds.
        self._integral = -_clamp(
            abs(self._integral), [self.integral_limits_min, self.integral_limits_max]
        )  # Avoid integral windup.
        self._derivative = -self.Kd * d_input / dt

    def __repr__(self):
        return ("{self.__class__.__name__}(" ")").format(self=self)

    @property
    def components(self):
        """
        The P-, I- and D-terms from the last computation as separate components as a tuple. Useful
        for visualizing what the controller is doing or when tuning hard-to-tune systems.
        """
        return self._proportional, self._integral, self._derivative

    @property
    def tunings(self):
        """The tunings used by the controller as a tuple: (Kp, Ki, Kd)."""
        return self.Kp, self.Ki, self.Kd

    @tunings.setter
    def tunings(self, tunings):
        """Set the PID tunings."""
        self.Kp, self.Ki, self.Kd = tunings

    @property
    def output_limits(self):
        """
        The current output limits as a 2-tuple: (lower, upper).

        See also the *output_limits* parameter in :meth:`PID.__init__`.
        """
        return self._min_output, self._max_output

    @output_limits.setter
    def output_limits(self, limits):
        """Set the output limits."""
        if limits is None:
            self._min_output, self._max_output = None, None
            return

        min_output, max_output = limits

        if (None not in limits) and (max_output < min_output):
            raise ValueError("lower limit must be less than upper limit")

        self._min_output = min_output
        self._max_output = max_output

        self._integral = _clamp(self._integral, self.output_limits)
        self._last_output = _clamp(self._last_output, self.output_limits)
