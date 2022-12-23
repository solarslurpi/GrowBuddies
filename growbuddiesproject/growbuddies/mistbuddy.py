#
# MistBuddy utilizes the readings from SnifferBuddy to calculate the appropriate length of time to activate the humidifier using a PID controller.
#
# Copyright 2022 Happy Day

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

from growbuddies.PID_code import PID
import logging
from enum import Enum
from growbuddies.gus import Gus
from growbuddies.snifferbuddyreadings import SnifferBuddyReadings
import threading
import signal


class growthStage(Enum):
    """An enumeration to let growBuddy know if the plants it is caring for are in the vegetative or flower growth stage.

    :param Enum: This setting can be either 'VEG' for the vegetative stage or 'FLOWER' for the flowering stage of the plant.

    """

    VEG = 2
    FLOWER = 3


class MistBuddy(Gus):

    """MistBuddy uses the readings from SnifferBuddy and a PID controller to calculate the ideal duration to turn on the humidifier in order to provide the plants with the optimal vapor pressure deficit (VPD) value. In addition to this, MistBuddy inherits various capabilities from Gus, such as the ability to log data and manage mqtt traffic.

    The ideal vpd level is determined from this vpd chart:

       .. image:: ../docs/images/vpd_chart.jpg
            :scale: 50
            :alt: Flu's vpd chart
            :align: center

    Args:
        :param snifferbuddy_status_callback: This callback function is activated when Gus (our mqtt broker) sends out a Last Will and Testament (LWT) mqtt message. The function is called with a string that indicates either "online" or "offline" status. If the returned string is "offline," it indicates that SnifferBuddy has not been sending mqtt messages. This callback function is optional and is set to "None" by default.

        :param growth_stage: This parameter specifies the growth stage of the plant, either vegetative or flowering. The default value is "growthStage.VEG."

        :param readings_table_name: A string that will be the name of the table (or a Measurement using influxdb terminology)  in InfluxDB containing SnifferBuddy readings, including vpd, while MistBuddy is running. By default, SnifferBuddy readings will not be stored.

        :param manage: A False setting for this parameter causes MistBuddy to refrain from turning the humidifier on and off. This can be helpful for initial debugging, but it has little effect on the PID controller's output. The default setting is True.

    Raises:
            The code checks if the vpd setpoint, which is read from the settings file, is within the expected range. If it is not, an exception is raised.

    """

    def __init__(
        self,
        snifferbuddy_status_callback=None,
        growth_stage=growthStage.VEG,
        readings_table_name=None,
        manage=True,
    ):
        # Set up for a Systemd stop command by setting up a SIGTERM handler
        # TODO: Not sure the SIGTERM is working.  Need to look more closely at shutdown.
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        # MistBuddy uses Gus to get SnifferBuddy values.
        super().__init__(
            readings_callback=self._values_callback,
            table_name=readings_table_name,
            status_callback=snifferbuddy_status_callback,
            log_level=logging.DEBUG,
        )
        self.manage = manage
        msg = "Managing vpd." if self.manage else "Observing vpd."
        self.logger.debug(msg)
        # Checking if the light changed from off to on.  If it did, the PID controller should know this so it can reset the error part
        # that accumulates.
        self.light_switched_on = None
        # Set up the setpoint to the ideal vpd value.
        self.setpoint = 0.0
        if growth_stage == growthStage.VEG:
            self.setpoint = self.settings["vpd_setpoints"]["veg"]
        else:
            self.setpoint = self.settings["vpd_setpoints"]["flower"]
        # The setpoint should be around .6 to 1.6...
        if not isinstance(self.setpoint, float) or self.setpoint * 10 not in range(20):
            raise Exception("The vpd setpoint should be a floating point number between 0.0 and less than 2.0")
        # These are used in the _pid() routine.
        self.pid_cum_error = 0.0
        self.pid_last_error = 0.0
        # Initialize the PID tuning variables.
        # How far away from the destination - Proportional
        Kp = self.settings["PID_settings"]["Kp"]
        Ki = self.settings["PID_settings"]["Ki"]
        Kd = self.settings["PID_settings"]["Kd"]
        # By default mqtt_time is used for time between sampling.
        clamp = (self.settings["PID_settings"]["output_limits"][0], self.settings["PID_settings"]["output_limits"][1])
        self.pid = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=self.setpoint, output_limits=(clamp))
        # The PID class as a __repr__() method.
        self.logger.debug(self.pid)

    def _values_callback(self, s: SnifferBuddyReadings):
        """growBuddy calls this method when it receives a reading from the requested sensor. vpd adjustment occurs during
        transpiration.  Transpiration is occuring when the grow lights are on.  The vpd will not be adjusted when the grow
        lights are off.

        Args:
            s (SnifferBuddyReadings): A reading from SnifferBuddy within an instance of SnifferBuddyReadings.
        """
        if (
            s.light_level > 700
        ):  # A light strong enough to start transpiration is assumed if the photoresister is between 700 and 1024.
            nSecondsON, error = self._pid(s.vpd)
            self.logger.debug(f"vpd: {s.vpd}   num seconds to turn humidifier on: {nSecondsON}. ")
            if self.manage and nSecondsON > 0:
                self._turn_on_mistBuddy(nSecondsON)

        if self.vpd_values_callback:
            self.vpd_values_callback(self.setpoint, s.vpd, nSecondsON, error)

    def _pid(self, reading: float) -> int:
        """This is the code for the PID controller.

        Args:
            reading (float): The vpd value that will be compared to the setpoint.

        Returns:
            int: The number of seconds to turn on mistBuddy.

        The goals of this PID controller are:

        * Automatically adjust the humidity within a grow tent to the vpd setpoint.

        * Be better than a "BANG-BANG" controller by not constantly turning mistBuddy on and off.


        More like **This**

        .. image:: ../docs/images/PID_controller.jpg
            :scale: 35
            :alt: PID Controller
            :align: center

        Than **This**

        .. image:: ../docs/images/bangbang_controller.jpg
            :scale: 30
            :alt: BANG BANG Controller
            :align: center

        .. note::
            I expect this method to evolve over time.

            - I am new to PID controllers.  I'm bumbling about tuning it.  My goal is to get advice from folks that know more than me,
              and then improve the code.

            - I am optimizing for my environment - a climate controlled area with a grow tent.  The temperature is in the 70's F.  The relative
              humidity is typically around 40-50%.
        """

        nSecondsOn, error = self.pid(reading)
        return nSecondsOn, error

    def _turn_on_mistBuddy(self, nSecondsON: int) -> None:
        """Send mqtt messages to mistBuddy's plugs to turn ON.

        Args:
            nSecondsON (int): The number of seconds to turn the plugs on.

        """
        # Set up a timer with the callback on completion.
        timer = threading.Timer(nSecondsON, self._turn_off_mistBuddy)
        # The command to a Sonoff plug can be either TOGGLE, ON, OFF.
        # Send the command to power ON.
        self.mqtt_client.publish(self.settings["mqtt"]["mistBuddy_fan_topic"], "ON")
        self.mqtt_client.publish(self.settings["mqtt"]["mistBuddy_mister_topic"], "ON")
        self.logger.debug(f"...Sent mqtt messages to the two mistBuddy plugs to turn ON for {nSecondsON} seconds.")
        timer.start()

    def _turn_off_mistBuddy(self):
        """The timer set in _turn_on_mistBuddy has expired.  Send messages to the
        mistBuddy plugs to turn OFF."""

        self.mqtt_client.publish(self.settings["mqtt"]["mistBuddy_fan_topic"], "OFF")
        self.mqtt_client.publish(self.settings["mqtt"]["mistBuddy_mister_topic"], "OFF")
        self.logger.debug("...Sent mqtt messages to the two mistBuddy plugs to turn OFF.")

    def _exit_gracefully(self):
        self._turn_off_mistBuddy(self)
        exit(0)
