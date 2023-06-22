#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
"""
=============================
Storing SnifferBuddy Readings
=============================
This script stores SnifferBuddy readings into an InfluxDB table. It requires a running
SnifferBuddy device sending MQTT messages and an MQTT broker (Gus). Run the script from
the command line (within your virtual environment) by typing `store-readings`.

"""
from growbuddies.mqtt_code import MQTTService
from growbuddies.settings_code import Settings
from growbuddies.snifferbuddyreadings_code import SnifferBuddyReadings
from growbuddies.logginghandler import LoggingHandler
from growbuddies.influxdb_code import ReadingsStore
import sys
import time

class Callbacks:
    """
    A class used to handle the two SnifferBuddy callbacks.

    This class is responsible for logging and storing readings and status updates
    from the SnifferBuddy device.

    Args:
        logger (LoggingHandler): Logger for debugging and error handling.
        table_to_store_readings (ReadingsStore): Database table to store SnifferBuddy readings.
    """

    def __init__(self) -> None:
        """
        Initialize the Callbacks class.

        Initializes the logger and the database table for storing readings.
        """
        self.logger: LoggingHandler = LoggingHandler()
        self.table_to_store_readings: ReadingsStore = ReadingsStore()

    def on_snifferbuddy_readings(self, mqtt_payload: str) -> None:
        """
        This callback function handles MQTT messages from SnifferBuddy.  The payload is a
        JSON string that is converted into a SnifferBuddyReadings object from the
        growbuddies.snifferbuddyreadings_code module.

        Args:
            mqtt_payload (str): The MQTT payload string with SnifferBuddy readings.

        """
        s: SnifferBuddyReadings = SnifferBuddyReadings(mqtt_payload)
        if s.valid_packet:
            self.logger.debug(
                f"SnifferBuddy Readings after a conversion from msg.payload {s.dict}"
            )
            self.table_to_store_readings.store_readings(s.dict)

    def on_snifferbuddy_status(self, status: str) -> None:
        """
        Log the online/offline status of the SnifferBuddy.

        Args:
            status (str): The status of SnifferBuddy, either "Online" or "Offline".
        """
        self.logger.debug(f"-> SnifferBuddy is: {status}")


def main() -> None:
    """
    This is the main entry point function of the store_readings application. The goal is to listen for SnifferBuddy MQTT messages. When one comes in, store the
    readings into the InfluxDB database table identified in the section discussing :ref:`GrowBuddies Settings <_growbuddies_settings>`.

    Here's a general description of what this function does:
    (Note: The first two points reference :ref:`GrowBuddies Settings <_growbuddies_settings>`)

    1. Initializes and loads application settings from a Settings object. The settings include the MQTT configurations such as broker address, port number, and topic names.

    2. Gathers callback methods associated with the "snifferbuddy_mqtt" service via the Settings object. The callbacks provide the actions to be performed upon receiving messages on the MQTT topics.

    3. Instantiates an MQTTService object with the gathered callback methods. This MQTTService object acts as the MQTT client, subscribing to and publishing messages on MQTT topics.

    4. Starts the MQTT service, which begins the process of listening to messages from the MQTT broker and calling the appropriate callback function as messages are received.

    5. Runs an infinite loop to keep the MQTT service running. The loop can be exited and the service stopped using a KeyboardInterrupt (e.g., Ctrl+C).

    Note:
    The main function does not take any arguments and does not return any values. It is meant to be invoked as the entry point of the application, typically if this module
"""
    settings = Settings()
    settings.load()
    callbacks = Callbacks()
    methods = settings.get_callbacks("snifferbuddy_mqtt", callbacks)
    mqtt_service = MQTTService(methods)
    mqtt_service.start()
    while True:
        try:
            pass
        except KeyboardInterrupt:
            # Stop the MQTT service
            mqtt_service.stop()
            sys.exit()
        time.sleep(5)  # chill...


if __name__ == "__main__":
    main()
