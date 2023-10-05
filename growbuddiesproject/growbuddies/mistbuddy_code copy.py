#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################

from growbuddies.PID_code import PID
from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings
from growbuddies.mqtt_code import MQTTClient
import threading
import time
from collections import deque


class MistBuddy:
    def __init__(self):
        """Initializes the MistBuddy class.

        This method sets up an MQTT client and a PID controller, and associates them with the MistBuddy instance. It also expects two MQTT topics (for fan power and mister power) from the application's settings, and raises an exception if they are not provided.

        Attributes:
            logger (LoggingHandler): An instance of the LoggingHandler for logging events.
            settings (Settings): An instance of the Settings class that loads the mistBuddy
            MQTT topics through the call to settings.get_callbacks().  In this case, a dict is
            returned that contains the MQTT topics for the keys and a blank string for the callbacks
            since MistBuddy does not use callbacks. : as defined in :ref:`growbuddies_settings.json  <_manage_vpd_settings>`
            fan_power_topic (str): The MQTT topic associated with the fan's power.
            mister_power_topic (str): The MQTT topic associated with the mister's power.
            mqtt_client (MQTTClient): An MQTT client initialized with the name "MistBuddy".
            pid (PID): A PID controller initialized with the key "MistBuddy_PID_key" found in
            :ref:`growbuddies_settings.json  <_manage_vpd_settings>`.

        Raises:
            Exception: If there are not exactly two MQTT topics provided (one for the fan power and one for the mister power).

        Debugging:
            Logs a debug message upon successful initialization.
        """
        self.logger = LoggingHandler()
        settings = Settings()
        settings.load()
        topics_and_methods = settings.get_callbacks("mistbuddy_mqtt", None)
        # We need a power topic for the fan and one for the mister.
        if len(topics_and_methods) != 2:
            raise Exception(
                f"ERROR - Expecting a topic for the fan power and a topic for the mister power.  Received {len(topics_and_methods)} topics."
            )
        self.mister_power_topic = topics_and_methods.popitem()[0]
        self.fan_power_topic = topics_and_methods.popitem()[0]
        # We use the mqtt client to send power on and off messages to the mistbuddy plugs.
        self.mqtt_client = MQTTClient("MistBuddy")
        # These are used in the _pid() routine.
        self.pid = PID("MistBuddy_PID_key")

        self.logger.debug(f"------- Finished Init of MistBuddy....PID Key: {self.pid}")
        # Get variables ready to hold a rolling window of values.
        # We use a rolling window and then an average of the values in logic control.  This makes having multiple snifferbuddies less chaotic.
        ROLLING_WINDOW_SIZE = 5
        self.vpd_values = deque(maxlen=ROLLING_WINDOW_SIZE)

    def adjust_humidity(self, vpd: float) -> None:
        """
        Adjust the humidity based on an average VPD reading over the
        secs_between_pid tuning.

        Args:
            vpd (float): Vapor Pressure Deficit value.
        """
        # Use an average from a rolling window.
        self.vpd_values.append(vpd)
        vpd_mean = sum(self.vpd_values)/len(self.vpd_values) if self.vpd_values else 0
        seconds_on = self.pid.calc_secs_on(vpd_mean)
        if seconds_on > 0.0:
            self.turn_on_mistBuddy(seconds_on)
        self.logger.debug(f"vpd from snifferbuddy: {vpd} average vpd value: {vpd_mean}")
    def _publish_power_plug_messages(self, power_state: int) -> None:
        """
        Publish MQTT messages to control power state of MistBuddy plugs.

        Args:
            power_state (int): Desired power state, either 1 (for on) or 0.
        """
        rcs = []
        rcs.append(self.mqtt_client.publish(self.fan_power_topic, power_state, qos=2))
        rcs.append(
            self.mqtt_client.publish(self.mister_power_topic, power_state, qos=2)
        )
        return rcs

    def turn_on_mistBuddy(self, seconds_on: float) -> None:
        """
        Turn on MistBuddy for a specified duration.

        Args:
            seconds_on (float): Duration to turn on MistBuddy in seconds.
        """
        # I was challenged because the power would be turned on but not off.  This got me to think there
        # was something wrong with threading.  But then I noticed the tasmotized devices were occassionally
        # not able to see Gus.  I had gotten a new wifi mesh and it doesn't seem to handle local ip names well.
        # gus.local was working until it is not.... so I had to hard code the ip address.  Yuk.

        # Set up a timer with the callback on completion.
        self.mqtt_client.start()
        timer = threading.Timer(seconds_on, self.turn_off_mistBuddy)
        # Start the client here, then stop in turn_off_mistbuddy
        self.logger.debug(f"MISTBUDDY ON FOR {seconds_on} SECONDS")

        self._publish_power_plug_messages(1)
        self.mqtt_client.stop()
        timer.start()

    def turn_off_mistBuddy(self) -> None:
        self.mqtt_client.start()
        self._publish_power_plug_messages(0)
        # Can't hurt to send another turn off...
        time.sleep(1)
        rcs = self._publish_power_plug_messages(0)
        for rc in rcs:
            if rc.rc == 0:
                self.logger.debug(f"Message {rc.mid} published successfully.")
            else:
                self.logger.debug(
                    f"Failed to publish message {rc.mid}. Return code: {rc.rc}"
                )
        self.mqtt_client.stop()
        self.logger.debug("MISTBUDDY OFF")
