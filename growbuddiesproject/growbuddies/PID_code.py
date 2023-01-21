#
# The PID controller returns how many seconds to turn the DIY humidifier on.
#
# Copyright 2023 Happy Day

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
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
    """This class is a modified version of the `simple-pid <https://github.com/m-lundberg/simple-pid>`_ package.  Thanks to the initial work of `Brett Beauregard and his Arduino PID controller as well as documentation <http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/>`_.  The modification uses the time between mqtt messages as the (fairly) consistent sampling time instead of the system clock.

    .. code-block:: json

        "vpd_growth_stage": "veg",
        "vpd_setpoints": {
            "veg": 0.9,
            "flower": 1.0
            }
        "PID_settings": {
        "Kp": 240,
        "Ki": 0.1,
        "Kd": 0.1,
        "output_limits": [0, 20],
        "integral_limits":[0, 7],
        "tolerance": 0.01
        }

    - The PID controller returns how many seconds to turn the DIY humidifier on.
    - MistBuddy turns the humidifier on for the number of seconds returned.  The humidifier is turned off after the number of seconds expires."""

    def __init__(self):
        """Initialize a new PID controller.  Instead of passing parameters into the constructor, the PID controller is
        initialized with values from the growbuddies_settings.file.:

        .. code-block:: python

            settings = Settings()
            settings.load()
            callbacks = Callbacks()
            methods = settings.get_callbacks("snifferbuddy_mqtt", callbacks)
            mqtt_service = MQTTService(methods)
            mqtt_service.start()


        .. code-block:: python

            "vpd_growth_stage": "veg",
            "vpd_setpoints": {
            "veg": 0.9,
            "flower": 1.0
            }



            Args:
                :vpd_growth_stage: The growth stage of the plants being cared for.  This can be either 'veg' or 'flower'.
                :vpd_setpoints: The setpoint for the PID controller.  This is the target value that the PID controller will
                attempt to achieve.If the vpd_growth_stage is set to 'veg', the setpoint will be 0.9.  If the vpd_growth_stage
                is set to 'flower', the setpoint will be 1.0.
                :Kp: The value for the proportional gain Kp.
                :Ki: The value for the integral gain Ki.
                :Kd: The value for the derivative gain Kd.

            .. note::
                 See :ref:`The section on PID tuning<PID_tuning>` for more information on tuning these values.
                :output_limits: Output limits can be specified as an iterable with two elements, such as (lower, upper).
                These limits ensure that the output will never exceed the upper limit. Either
                limit can be set to None if there is no limit in that direction.
                :integral_limits: Integral limits can be specified as an iterable with two elements, such as (lower, upper).
                These limits ensure that the integral will never exceed the upper limit. Either limit can be set to None if there is no limit in that direction.
                :tolerance: If the vpd_current is within the tolerance of the setpoint, the PID controller will return 0 for the number of
                seconds to turn the humidifier on.

        """

        self.logger = LoggingHandler()
        # Load the settings discussed above from growbuddies_settings.json.
        settings = Settings()
        settings.load()
        pid_settings = settings.get("PID_settings")
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

        self.auto_tune = True  # Used in the pid routine to raise up the K values as needed.

        self.output_limits = pid_settings["output_limits"][0], pid_settings["output_limits"][1]

    def __call__(self, vpd_current):

        """Update the PID controller with the vpd value just calculated from the latest SnifferBuddyReading and figure out
        how many seconds to turn on the humidifier if the vpd value is above the vpd setpoint (i.e.: ideal)
        value.  0 seconds is returned if the vpd value is and calculate and return a control output if
        sample_time seconds has passed since the last update.

        Args:
            :vpd_current: The most recent vpd value calculated from the latest SnifferBuddyReading.
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
        error = self.setpoint - vpd_current
        d_vpd = vpd_current - (self._last_vpd if (self._last_vpd is not None) else vpd_current)
        self._compute_terms(d_vpd, error, dt)
        self.logger.debug(
            f"error: {error:.2f}, P: {self._proportional:.2f}, I: {self._integral:.2f}, D: {self._derivative:.2f}"
        )
        # It is getting too humid.  Since we only have a humidifier to adjust, we return.
        if error > self.tolerance:
            return 0, 0
        # Do a bit of autotuning until it grows to big.  Cap it when the air gets too moist.
        # used for the Ziegler-Nichols method of tuning.
        # if error < self.tolerance and self.auto_tune:
        #      self.Kp += 1

        self.logger.debug(f"K values: Kp {self.Kp} Ki {self.Ki}  Kd {self.Kd}")
        #     # self.Ki += 0.05
        #     # self.Kd += 0.01
        #     self.logger.debug(f"***>updating coefficients Kp {self.Kp} Ki {self.Ki}  Kd {self.Kd}")
        # else:
        #     self.logger.debug(f"***>NOT updating coefficients Kp {self.Kp} Ki {self.Ki}  Kd {self.Kd}")

        # Compute number of seconds to turn on mistBuddy, which is 0 or a positive number of seconds.

        output = abs(self._proportional + self._integral + self._derivative)
        nSecondsOn = int(round(output))
        nSecondsOn = _clamp(nSecondsOn, self.output_limits)
        self.logger.debug(f" nSecondsOn is {nSecondsOn}")

        # Keep track of state
        self._last_output = output
        self._last_vpd = vpd_current
        self._prev_error = error
        return nSecondsOn, error

    def _compute_terms(self, d_vpd, error, dt):
        """Compute the integral and derivative terms.  Clamp the integral term to prevent it from growing too large.

        Args:
            :d_vpd (float): The difference between the current and previous vpd values.  Used by the derivative term.
            :error (float): The difference between the current vpd value and the setpoint.  Used by the proportional
             integral term.
            :dt (float): The difference in time between the current and previous vpd values.  Used by the integral and
             derivative terms.
        """
        # Compute integral and derivative terms
        # Since we are not using PID during the night, we reset the error terms and start over.
        self._proportional = self.Kp * error
        self._integral += self.Ki * error * dt
        # I can see how the integral value forces the steady state the Kp gain brought closer to the setpoint.
        # However, the Ki terms seems to grow to a devastatingly large number which causes oscillation.  From
        # watching the vpd values, having an ability to clamp the integral term seems to help.
        self._integral = -_clamp(abs(self._integral), [self.integral_limits_min, self.integral_limits_max])
        self._derivative = -self.Kd * d_vpd / dt

    def __repr__(self):
        return (
            f"PID settings:\n"
            f"  Kp = {self.Kp}\n"
            f"  Ki = {self.Ki}\n"
            f"  Kd = {self.Kd}\n"
            f"  setpoint = {self.setpoint}\n"
            f"  output limits = ({self.output_limits_min}, {self.output_limits_max})\n"
            f"  integral limits = ({self.integral_limits_min}, {self.integral_limits_max})\n"
            f"  tolerance = {self.tolerance}"
        )

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
