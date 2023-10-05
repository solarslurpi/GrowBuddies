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
from growbuddies.logginghandler import LoggingHandler
from growbuddies.store_readings import ReadingsStore
import time
import warnings
import threading


COMPARISON_FUNCTIONS = {
    "greater_than": lambda x, max_val: x > max_val,
    "less_than": lambda x, max_val: x < max_val,
}

TUNE_STABILITY_TIME = 60 * 15

try:
    # Get monotonic time to ensure that time deltas are always positive
    _current_time = time.monotonic
except AttributeError:
    # time.monotonic() not available (using python < 3.3), fallback to time.time()
    _current_time = time.time
    warnings.warn(
        "time.monotonic() not available in python < 3.3, using time.time() as fallback"
    )


def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    value = abs(
        value
    )  # The direction to move might be up or down. But n seconds is always positive.
    if (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value


class PID(object):
    def __init__(self, pid_dict: dict):
        self.logger = LoggingHandler()
        self._min_output, self._max_output = None, None
        self._last_value = None

        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._prev_error = None

        self._last_time = _current_time()
        self._last_output = None
        self.pid_table = None
        self.tune_timer = None


        try:
            self.Kp = pid_dict["Kp"]
            self.Ki = pid_dict["Ki"]
            self.Kd = pid_dict["Kd"]
            self.setpoint = pid_dict["setpoint"]
            self.logger.debug(
                f"==> SetPoint: {self.setpoint} Kp: {self.Kp} Ki: {self.Ki} Kd: {self.Kd}"
            )
            self.output_limits = tuple(pid_dict["output_limits"])
            self.tune_increment = pid_dict["tune"]["increment"]
            if len(pid_dict["tune"]["influxdb_table_name"]) >0:
                self.pid_table = ReadingsStore(pid_dict["tune"]["influxdb_table_name"])

            self.integral_limits = tuple(pid_dict["integral_limits"])

            if pid_dict["comparison_function"] == "greater_than":
                self.sign = 1
            else:
                self.sign = -1

            if self.tune_increment:
                self.start_timer()
        except KeyError as e:
            self.logger.error(
                f"ERROR: The {e} key was not found in pid_dict.  Please see growbuddies_settings.json."
            )
            raise e

    def start_timer(self) -> None:
        self.tune_timer = threading.Timer(TUNE_STABILITY_TIME, self.update_kp)
        self.tune_timer.start()

    def update_kp(self) -> None:
        self.Kp += self.tune_increment
        self.start_timer()

    def calc_secs_on(self, current_value) -> float:
        """Update the PID controller with the vpd value just calculated from the latest SnifferBuddyReading and figure out
        how many seconds to turn on the humidifier if the vpd value is above the vpd setpoint (i.e.: ideal)
        value.  0 seconds is returned if the vpd value is and calculate and return a control output if
        sample_time seconds has passed since the last update.

        Args:
            :current_value: The most recent vpd value calculated from the latest SnifferBuddyReading.
        """
        # Determine if it is time to tune.
        now = time.monotonic()
        # if dt doesn't exist, it's the first time through. There is no self._last_time yet.
        try:
            dt
        except NameError:
            dt = now - self._last_time if (now - self._last_time) else 1e-16
        self.logger.debug(f"--> In the PID CONTROLLER.  {dt} seconds have elapsed since the last reading.")
        self._last_time = now


        # self.logger.debug(f"K values: Kp {self.Kp} Ki {self.Ki}  Kd {self.Kd}")
        # Compute error terms - Note: The error continues to accumulate (integral and derivative) so that when
        # the error goes within the range that the actuator can address, the response will be faster.
        d_value = current_value - (
            self._last_value if (self._last_value is not None) else current_value
        )
        error = self.setpoint - current_value
        self._compute_terms(d_value, error, dt)
        self.logger.debug(
            f"error: {error:.2f}, P: {self._proportional:.2f}, I: {self._integral:.2f}, D: {self._derivative:.2f}"
        )

        self.logger.debug(f"K values: Kp {self.Kp} Ki {self.Ki}  Kd {self.Kd}")

        output = self._proportional + self._integral + self._derivative

        # Keep track of state
        self._last_output = output
        self._last_value = current_value
        self._prev_error = error
        output = _clamp(output, self.output_limits)
        if self.pid_table:
            pid_table_row = {
                'Kp': self.Kp,
                'Ki': self.Ki,
                'Kd': self.Kd,
                'value': current_value
            }
            self.pid_table.store_readings(pid_table_row)
        return output

    def _compute_terms(self, d_value, error, dt):
        """Compute the integral and derivative terms.  Clamp the integral term to prevent it from growing too large."""
        # Compute integral and derivative terms
        # Since we are not using PID during the night, we reset the error terms and start over.
        self._proportional = self.Kp * error
        self._integral += self.Ki * error * dt
        # I can see how the integral value forces the steady state the Kp gain brought closer to the setpoint.
        # However, the Ki terms seems to grow to a devastatingly large number which causes oscillation.  From
        # watching the vpd values, having an ability to clamp the integral term seems to help.
        self.logger.debug(f"*****>>> Integral value: {self._integral}")
        self._integral = self.sign*_clamp(abs(self._integral), self.integral_limits)
        self._derivative = self.sign*self.Kd * d_value / dt


    def __repr__(self):
        return (
            f"PID settings:\n"
            f"  Kp = {self.Kp}\n"
            f"  Ki = {self.Ki}\n"
            f"  Kd = {self.Kd}\n"
            f"  setpoint = {self.setpoint}\n"
            f"  output_limits = ({self.output_limits}, {self.output_limits})\n"
            f"  integral_limits = ({self.integral_limits})\n"
            f"  tune = {self.tune_increment}\n"
            f"  comparison_function = {self.comparison_func}\n"
        )

    @property
    def current_values_dict(self):
        """Return a dictionary of current values."""
        return {
            # add in P, I and D terms from the last computation.
            "P": self._proportional,
            "I": self._integral,
            "D": self._derivative,
            "Kp": self.Kp,
            "Ki": self.Ki,
            "Kd": self.Kd,
        }

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


