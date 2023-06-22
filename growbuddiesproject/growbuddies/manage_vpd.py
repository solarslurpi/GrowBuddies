#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################

from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings
from growbuddies.mqtt_code import MQTTService
from growbuddies.snifferbuddyreadings_code import SnifferBuddyReadings
from growbuddies.mistbuddy_code import MistBuddy
import sys
import time


class Callbacks:
    """The Callbacks class contains two callback functions that are passed to `MQTTServer`. These functions
    are activated when MQTTService receives an `on_message` event for the corresponding topics associated with
    the callbacks.
    """

    def __init__(self):
        self.logger = LoggingHandler()
        self.mistbuddy = MistBuddy()

    def on_snifferbuddy_readings(self, msg):
        """
        This callback function handles MQTT messages from SnifferBuddy.  The payload is a
        JSON string that is converted into a SnifferBuddyReadings object from the
        growbuddies.snifferbuddyreadings_code module.

        Methods from the growbuddies.mistbuddy_code module are then called to adjust the humidity based on the vpd value.

        Args:
            mqtt_payload (str): The MQTT payload string with SnifferBuddy readings.

        """
        # Translate the mqtt message into a SnifferBuddy class.
        s = SnifferBuddyReadings(msg)
        if s.valid_packet:
            self.logger.debug(f"the snifferbuddy values: {s.dict}")
            # The light level is a string either "ON" or "OFF".
            on_or_off_str = s.light_level.upper()
            self.logger.debug(f"The light is {on_or_off_str}")
            # Adjust vpd. vpd is most relevant when the plants are transpiring when the lights are on.
            if on_or_off_str == "ON":
                self.mistbuddy.adjust_humidity(s.vpd)

    # The vpd value is returned. Turn on and off the humidifier based on it's value.

    def on_snifferbuddy_status(self, status):
        """

        .. note::

           How SnifferBuddy's status is determined is discussed in :ref:`mqtt_LWT`.


        "This callback function handles MQTT Last Will and Testament (LWT) messages regarding the online status of SnifferBuddy,
        which can be either "online" or "offline."

        Args:
            status (str): Either the string "Online" or "Offline".
        """
        self.logger.debug(f"-> SnifferBuddy is: {status}")
        # TODO: send alert if offline since snifferbuddy readings are the heartbeat.



def main():
    """
    This is the main entry point function of the `manage_vpd` script.  The primary role of `manage_vpd` is to maintain the vpd setpoint set in the :ref:`GrowBuddies Settings <_manage_vpd_settings>` file when the LED lights are on.

    The vpd is maintained with a two step process:
    1. Get vpd readings from SnifferBuddy.
    2. Use MistBuddy to maintain the vpd to the vpd setpoint by turning on and off a humidifier.

    The first step is handled identically to the method used in the :ref:`store_readings.py <_store_readings_code>` script.  Callbacks are set up each subscribed to receive SnifferBuddy MQTT messages.


    However, instead of storing the SnifferBuddy readings into an influxdb table, `manage_vpd.py` calls into :ref:`MistBuddy <mistbuddy.md>` to maintain the vpd setpoint identified in the :ref:`GrowBuddies Settings <_growbuddies_settings>` file.

    When SnifferBuddy readings are received by the call back, it is sent to the MistBuddy code. MistBuddy figures out if the vpd values are higher than the setpoint.  If they are, MistBuddy turn on the humidifier for enough time to maintain the vpd setpoint value.
    """
    settings = Settings()
    settings.load()
    obj = Callbacks()
    methods = settings.get_callbacks("snifferbuddy_mqtt", obj)
    mqtt_service = MQTTService(methods)
    mqtt_service.start()
    while True:
        try:
            pass
        except KeyboardInterrupt:
            # Stop the MQTT service
            mqtt_service.stop()
            sys.exit()
        time.sleep(5) # Take a break.


if __name__ == "__main__":
    main()
