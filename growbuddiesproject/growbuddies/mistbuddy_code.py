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
from growbuddies.logginghandler import LoggingHandler
from growbuddies.snifferbuddyreadings_code import SnifferBuddyReadings
from growbuddies.settings_code import Settings
from growbuddies.mqtt_code import MQTTClient
import threading


class MistBuddy:

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
        manage=True,
    ):
        self.logger = LoggingHandler()

        self.manage = manage
        msg = "Managing vpd." if self.manage else "Observing vpd."
        self.logger.debug(msg)
        settings = Settings()
        settings.load()
        topics_and_methods = settings.get_callbacks("mistbuddy_mqtt_dict", None)
        # We need a power topic for the fan and one for the mister.
        if len(topics_and_methods) != 2:
            raise Exception(
                f"ERROR - Expecting a topic for the fan power and a topic for the mister power.  Received {len(topics_and_methods)} topics."
            )
        self.fan_power_topic, value = topics_and_methods.popitem()
        self.mister_power_topic, value = topics_and_methods.popitem()

        # These are used in the _pid() routine.
        self.pid_cum_error = 0.0
        self.pid_last_error = 0.0
        self.pid = PID()

        self.logger.debug(self.pid)

    def isLightOn(self, light_level) -> bool:
        # Reading if the light level represents on depends if the photoresistor circuit
        # was made with a pull up or pull down resistor.  Mine is pullup, so the light is
        # on when the number is low
        if light_level < 50:  # I noticed a value of 18 when it was on...so adding for ambient light.
            return True
        else:
            return False

    def adjust_humidity(self, s: SnifferBuddyReadings):
        """This method is called when a SnifferBuddy readings comes in.  Transpiration is occuring when the grow lights are on.  The vpd will not be adjusted when the grow
        lights are off.

        Args:
            s (SnifferBuddyReadings): A reading from SnifferBuddy within an instance of SnifferBuddyReadings.
        """

        nSecondsON, error = self._pid(s.vpd)
        self.logger.debug(f"vpd: {s.vpd}   num seconds to turn humidifier on: {nSecondsON}. The error is {error}")
        if self.manage and nSecondsON > 0:
            self._turn_on_mistBuddy(nSecondsON)

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
        mqtt_client = MQTTClient("MistBuddy")
        mqtt_client.start()
        mqtt_client.publish(self.fan_power_topic, "ON")
        mqtt_client.publish(self.mister_power_topic, "ON")
        mqtt_client.stop()
        self.logger.debug(f"...Sent mqtt messages to the two mistBuddy plugs to turn ON for {nSecondsON} seconds.")
        timer.start()

    def _turn_off_mistBuddy(self):
        """The timer set in _turn_on_mistBuddy has expired.  Send messages to the
        mistBuddy plugs to turn OFF."""
        mqtt_client = MQTTClient("MistBuddy")
        mqtt_client.start()
        mqtt_client.publish(self.fan_power_topic, "OFF")
        mqtt_client.publish(self.mister_power_topic, "OFF")
        mqtt_client.stop()
        self.logger.debug("...Sent mqtt messages to the two mistBuddy plugs to turn OFF.")
