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
from growbuddies.settings_code import Settings
from growbuddies.mqtt_code import MQTTClient
import threading


class MistBuddy:
    def __init__(self):
        """Initialize MistBuddy, set up an MQTT client and PID controller."""
        self.logger = LoggingHandler()
        settings = Settings()
        settings.load()
        topics_and_methods = settings.get_callbacks("mistbuddy_mqtt", None)
        # We need a power topic for the fan and one for the mister.
        if len(topics_and_methods) != 2:
            raise Exception(
                f"ERROR - Expecting a topic for the fan power and a topic for the mister power.  Received {len(topics_and_methods)} topics."
            )
        self.fan_power_topic = topics_and_methods.popitem()[0]
        self.mister_power_topic = topics_and_methods.popitem()[0]
        # We use the mqtt client to send power on and off messages to the mistbuddy plugs.
        self.mqtt_client = MQTTClient("MistBuddy")
        # These are used in the _pid() routine.
        self.pid = PID("MistBuddy_PID_key")

        self.logger.debug(f"------- Finished Init of MistBuddy....PID Key: {self.pid}")

    def adjust_humidity(self, vpd: float) -> None:
        """
        Adjust the humidity based on an average VPD reading over the
        secs_between_pid tuning.

        Args:
            vpd (float): Vapor Pressure Deficit value.
        """

        seconds_on = self.pid.calc_secs_on(vpd)
        self.logger.debug(f"Turn humidifier on: {seconds_on}. ")
        if seconds_on > 0.0:
            self.turn_on_mistBuddy(seconds_on)

    def _publish_power_plug_messages(self, power_state: str) -> None:
        """
        Publish MQTT messages to control power state of MistBuddy plugs.

        Args:
            power_state (str): Desired power state, either "ON" or "OFF".
        """
        self.mqtt_client.publish(self.fan_power_topic, power_state, qos=2)
        self.mqtt_client.publish(self.mister_power_topic, power_state, qos=2)

    def turn_on_mistBuddy(self, seconds_on: float) -> None:
        """
        Turn on MistBuddy for a specified duration.

        Args:
            seconds_on (float): Duration to turn on MistBuddy in seconds.
        """
        # Set up a timer with the callback on completion.
        timer = threading.Timer(seconds_on, self.turn_off_mistBuddy)
        # Start the client here, then stop in turn_off_mistbuddy
        self.mqtt_client.start()
        self._publish_power_plug_messages("ON")
        timer.start()
        self.logger.debug(f"...Sent mqtt messages to the two mistBuddy plugs to turn ON for {seconds_on} seconds.")

    def turn_off_mistBuddy(self) -> None:
        self._publish_power_plug_messages("OFF")
        self.mqtt_client.stop()
        self.logger.debug("...Sent mqtt messages to the two mistBuddy plugs to turn OFF.")
