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


class StomaBuddy:
    def __init__(self, method_dict):
        self.logger = LoggingHandler()

        settings = Settings()
        settings.load()
        self.method_dict = method_dict
        topics_and_methods = settings.get_callbacks("stomabuddy_mqtt", None)
        self.power_topic = list(topics_and_methods.keys())[0]
        self.logger.debug(f"The Power topic is: {self.power_topic}")

        # These are used in the _pid() routine.
        self.pid = PID("StomaBuddy_PID_key")
        # mqtt messages turn the co2 solenoid on and off.
        self.mqtt_client = MQTTClient("StomaBuddy")
        self.logger.debug(self.pid)

    def adjust_co2(self, co2_level: float) -> None:
        """This method calls the PID controller and turns the humidifier on if the PID controller determines that the vpd is too low.

        Args:
            vpd (float): The most current vpd reading.
        """
        # Do this first before any increments of Kp by the PID.
        if self.method_dict:
            pid_values = self.pid.current_values_dict
            key, callback_method = list(self.method_dict.items())[0]
            callback_method(pid_values)
            self.logger.debug(f"...Callback method called: {key}")

        seconds_on = self.pid.calc_secs_on(co2_level)

        # Log the vpd and nSecondsON with error
        self.logger.debug(f"Turn co2 solenoid on for : {seconds_on} seconds. ")
        if seconds_on > 0:
            self.turn_on_stomaBuddy(seconds_on)

    def turn_on_stomaBuddy(self, seconds_on: int) -> None:
        # Set up a timer with the callback on completion.
        timer = threading.Timer(seconds_on, self.turn_off_stomaBuddy)
        # The command to a Sonoff plug can be either TOGGLE, ON, OFF.
        self.mqtt_client.start()
        self.mqtt_client.publish(self.power_topic, "ON", qos=2)
        timer.start()
        self.logger.debug(
            f"...Sent mqtt message to topic: {self.power_topic} to turn ON for {seconds_on} seconds."
        )

    def turn_off_stomaBuddy(self) -> None:
        self.mqtt_client.publish(self.power_topic, "OFF", qos=2)
        self.mqtt_client.stop()
        self.logger.debug(
            f"...Sent mqtt messages to topic: {self.power_topic} to turn OFF."
        )
