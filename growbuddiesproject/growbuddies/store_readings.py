#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
"""
This script stores SnifferBuddy readings into an InfluxDB table. It requires a running
SnifferBuddy device sending MQTT messages and an MQTT broker (Gus). Run the script from
the command line (within your virtual environment) by typing `store-readings`.  For continuous running, use SystemD with the `store_readings.service` file.

"""
from growbuddies.snifferbuddy_handler import SnifferBuddyHandler
from growbuddies.influxdb_code import ReadingsStore
from growbuddies.logginghandler import LoggingHandler
import time

logger = LoggingHandler()
readings_store = ReadingsStore()


def store_readings(dict: dict) -> bool:
    """
    This function takes the message and stores it into a table within an InfluxDB
    database.

    The :ref:`GrowBuddies Settings <_growbuddies_settings>` properties:

    - "hostname"  (default = "gus")
    - "db_name"   (default = "gus")
    - "snifferbuddy_table_name" (default = "SnifferBuddy_Readings")

    are used within the ReadingsStore() class to know where to store the reading.
    Note: Before invoking this function, an instance of the ReadingsStore class was created using "my_table_name" as an argument. This instance represents the specific InfluxDB table where the readings will be stored.
    """

    try:
        readings_store.store_readings(dict)
        logger.debug(f"Readings stored: {dict}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}. Could not store the reading. ")
        return False


def main() -> None:
    """ "
    The main function for storing SnifferBuddy readings into an InfluxDB table.

    This function initializes a SnifferBuddyHandler and starts listening for SnifferBuddy readings.
    It continuously checks the handler's message queue for new SnifferBuddy readings. If a new reading
    is available, it gets stored in an InfluxDB table using the `store_readings` function.
    The function runs indefinitely until it is interrupted with a KeyboardInterrupt (Ctrl+C),
    at which point it stops the handler and exits.
    """
    handler = SnifferBuddyHandler()
    # Start listening for SnifferBuddy readings.
    handler.start()

    try:
        while True:
            message = handler.get_message_from_queue()
            if message is not None:
                message_type, message_content = message
                if message_type == "readings":
                    store_readings(message_content)

            time.sleep(5)
    except KeyboardInterrupt:
        handler.stop()


if __name__ == "__main__":
    main()
