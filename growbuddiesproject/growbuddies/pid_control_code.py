import time
import logging


class PID_Control:
    def __init__(
        self, Kp, Ki, Kd, setpoint, output_limits, integral_limits, comparison_function
    ):
        """
        Initialize the PID_Control class.

        Args:
        Kp, Ki, Kd (float): Initial PID coefficients.
        setpoint (float): Desired setpoint value.
        output_limits (tuple): Tuple of (min_output, max_output).
        integral_limits (tuple): Tuple of (min_integral, max_integral).
        comparison_function (function): Function to compare current value with setpoint.
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.output_limits = output_limits
        self.integral_limits = integral_limits
        self.comparison_function = comparison_function

        self._integral = 0
        self._last_error = 0
        self._last_time = None

        self.logger = logging.getLogger(__name__)
        self.first_run = True

    def update_tunings(self, Kp=None, Ki=None, Kd=None):
        """Update PID tunings."""
        if Kp is not None:
            self.Kp = Kp
        if Ki is not None:
            self.Ki = Ki
        if Kd is not None:
            self.Kd = Kd

    def calc_control_output(self, current_value):
        """
        Calculate the control output based on the current value.

        Args:
        current_value (float): The current value from the process.

        Returns:
        float: The control output.
        """
        # First run handling
        if self.first_run:
            self._last_time = time.time()
            self._last_error = self.setpoint - current_value
            self.first_run = False
            return 0

        current_time = time.time()
        dt = current_time - self._last_time

        # Avoid division by zero
        if dt <= 0:
            self.logger.warning(
                "Time difference 'dt' is non-positive. Skipping this calculation."
            )
            return 0

        error = self.setpoint - current_value

        # Proportional term
        proportional = self.Kp * error

        # Integral term
        self._integral += self.Ki * error * dt
        self._integral = max(
            min(self._integral, self.integral_limits[1]), self.integral_limits[0]
        )

        # Derivative term
        derivative = self.Kd * (error - self._last_error) / dt

        # Update last error and time
        self._last_error = error
        self._last_time = current_time

        # Compute output
        output = proportional + self._integral + derivative

        # Clamp output within limits
        output = max(min(output, self.output_limits[1]), self.output_limits[0])

        # Check with comparison function
        if self.comparison_function(current_value, self.setpoint):
            self.logger.info(
                "Comparison function condition met. Output might be modified."
            )
            # Additional logic can be implemented here based on the specific requirements

        return output

    def __repr__(self):
        return (
            f"<PID_Control Kp={self.Kp}, Ki={self.Ki}, Kd={self.Kd}, "
            f"Setpoint={self.setpoint}, OutputLimits={self.output_limits}, "
            f"IntegralLimits={self.integral_limits}>"
        )
