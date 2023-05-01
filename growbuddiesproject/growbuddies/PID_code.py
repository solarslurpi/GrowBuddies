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
from growbuddies.settings_code import Settings
from growbuddies.logginghandler import LoggingHandler
import time
import warnings
import json

COMPARISON_FUNCTIONS = {"greater_than": lambda x, max_val: x > max_val, "less_than": lambda x, max_val: x < max_val}


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
    value = abs(value)  # The direction to move might be up or down. But n seconds is always positive.
    if (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value


class PID(object):
    def __init__(self, PID_key: str):
        self.logger = LoggingHandler()
        if PID_key is None:
            self.logger.error("No PID_KEY was passed in.")
            raise ValueError("PID_key cannot be None.  Please see growbuddies_settings.json")
        self.PID_key = PID_key
        self._min_output, self._max_output = None, None
        self._last_value = None

        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._prev_error = None

        self._last_time = _current_time()
        self._last_output = None
        # Used to determine if it is time to tune
        self._reset()
        # Load the settings discussed above from growbuddies_settings.json.
        settings = Settings()
        settings.load()
        pid_settings = settings.get(self.PID_key)
        if pid_settings is None:
            self.logger.error("The PID_KEY was invalid.  Please see growbuddies_settings.json.")
            raise KeyError(f"{self.PID_key} not found in settings dictionary")

        try:
            self.Kp = pid_settings["Kp"]
            self.Ki = pid_settings["Ki"]
            self.Kd = pid_settings["Kd"]
            self.maximum = pid_settings["maximum"]
            self.setpoint = pid_settings["setpoint"]
            self.output_limits = tuple(pid_settings["output_limits"])
            self.tune_increment = pid_settings["tune"]["increment"]
            self.tune_start_stop_json = pid_settings["tune"]["start_stop_json"]
            self.integral_limits = tuple(pid_settings["integral_limits"])
            self.comparison_func = COMPARISON_FUNCTIONS.get(pid_settings["comparison_function"])
            self.secs_between_pid = pid_settings["secs_between_pid"]
        except KeyError as e:
            self.logger.error(f"ERROR: The {e} key was not found in the PID_KEY.  Please see growbuddies_settings.json.")
            raise e
        # The maximum property is how much greater than the setpoint can the value go up to (I did this to somewhat
        # accomodate drift.).  Thus, maximum must be greater than or equal to the setpoint
        if self.maximum < self.setpoint:
            self.logger.error(
                f"ERROR: The maximum property: {self.maximum} "
                f"is less than the setpoint: {self.setpoint}. "
                f"The maximum property is what is the maximum "
                f"value to be tolerated before adjusting."
            )

        if self.tune_increment > 0:
            self.logger.debug(f"Writing the start time to the file {self.tune_start_stop_json}")
            with open(self.tune_start_stop_json, 'w') as f:
                data = {'start_time': int(time.time())}
                json.dump(data, f)


    def _on_exit(self):
        if self.tune_increment > 0:
            self.logger.debug(f"Writing the start time to the file {self.tune_start_stop_json}")
            with open(self.tune_start_stop_json, 'a') as f:
                data = {'start_time': int(time.time())}
                json.dump(data, f)



    def _reset(self):
        """Reset the value accumulation and timer."""
        self.last_call_time = time.monotonic()
        self.average_value = 0
        self.sample_count = 0

    def calc_secs_on(self, current_value) -> float:
        """Update the PID controller with the vpd value just calculated from the latest SnifferBuddyReading and figure out
        how many seconds to turn on the humidifier if the vpd value is above the vpd setpoint (i.e.: ideal)
        value.  0 seconds is returned if the vpd value is and calculate and return a control output if
        sample_time seconds has passed since the last update.

        Args:
            :current_value: The most recent vpd value calculated from the latest SnifferBuddyReading.
        """
        # Determine if it is time to tune.
        current_time = time.monotonic()
        time_elapsed = current_time - self.last_call_time
        if time_elapsed < self.secs_between_pid:
            self.sample_count += 1
            self.average_value += (current_value - self.average_value) / self.sample_count
            self.logger.debug(
                f"--> Time Elapsed: {time_elapsed}, secs between pid tuning: {self.secs_between_pid} average value: {self.average_value}"
            )
            # Not tuning, so return 0 seconds.
            return 0
        else:
            self._reset()
        now = _current_time()
        # if dt doesn't exist, it's the first time through. There is no self._last_time yet.
        try:
            dt
        except NameError:
            dt = now - self._last_time if (now - self._last_time) else 1e-16
        self.logger.debug(f"--> In the PID CONTROLLER.  {dt} seconds have elapsed since the last reading.")
        self._last_time = now
        # Compute error terms - Note: The error continues to accumulate (integral and derivative) so that when
        # the error goes within the range that the actuator can address, the response will be faster.
        d_value = current_value - (self._last_value if (self._last_value is not None) else current_value)
        error = self.setpoint - current_value
        self._compute_terms(d_value, error, dt)
        self.logger.debug(
            f"error: {error:.2f}, P: {self._proportional:.2f}, I: {self._integral:.2f}, D: {self._derivative:.2f}"
        )
        # If the below is true, don't take action because the current value is higher than the setpoint by more than
        # the maximum value. This is done because there is no actuator to remove CO2 or humidity in the system.
        self.logger.debug(f"current value: {current_value:.2f} > maximum value {self.maximum}? ")
        if self.comparison_func(current_value, self.maximum):
            self.logger.debug("No actuator action needed.  Returning.")
            return 0.0

        # If self.tune_increment is not 0, change the Kp value in support of tuning the Kp value, for example during Ziegler-Nichols tuning.
        # Set tune = 0 in the json setting file to not adjust Kp.
        self.Kp += self.tune_increment

        self.logger.debug(f"K values: Kp {self.Kp} Ki {self.Ki}  Kd {self.Kd}")

        output = self._proportional + self._integral + self._derivative

        # Keep track of state
        self._last_output = output
        self._last_value = current_value
        self._prev_error = error
        output = _clamp(output, self.output_limits)
        return output

    def _compute_terms(self, d_value, error, dt):
        """Compute the integral and derivative terms.  Clamp the integral term to prevent it from growing too large.

        """
        # Compute integral and derivative terms
        # Since we are not using PID during the night, we reset the error terms and start over.
        self._proportional = self.Kp * error
        self._integral += self.Ki * error * dt
        # I can see how the integral value forces the steady state the Kp gain brought closer to the setpoint.
        # However, the Ki terms seems to grow to a devastatingly large number which causes oscillation.  From
        # watching the vpd values, having an ability to clamp the integral term seems to help.
        self._integral = -_clamp(abs(self._integral), self.integral_limits)
        self._derivative = -self.Kd * d_value / dt

    def __repr__(self):
        return (
            f"PID settings:\n"
            f"  Kp = {self.Kp}\n"
            f"  Ki = {self.Ki}\n"
            f"  Kd = {self.Kd}\n"
            f"  setpoint = {self.setpoint}\n"
            f"  output limits = ({self.output_limits}, {self.output_limits})\n"
            f"  integral limits = ({self.integral_limits})\n"
            f"  maximum value = {self.maximum}\n"
            f"  tune = {self.tune_increment}\n"
            f"  comparison function = {self.comparison_func}\n"
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
