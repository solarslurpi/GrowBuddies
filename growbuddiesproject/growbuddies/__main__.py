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


class Callbacks:
    def __init__(self):
        self.logger = LoggingHandler()

    def on_snifferbuddy_readings(self, mqtt_payload: str):
        """
        Process SnifferBuddy readings from the MQTT payload and store them in InfluxDB.
        """
        # 1. Convert mqtt payload string into a SnifferBuddy() class.
        s = SnifferBuddyReadings(mqtt_payload)
        if s.valid_packet:
            self.logger.debug(f"SnifferBuddy Readings after a conversion from msg.payload {s.dict}")
            # 2. Store the Readings into an influxdb measurement table.
            table_to_store_readings = ReadingsStore()
            # If successful and debug logging level is set, store_readings() will print out the success or failure message.
            table_to_store_readings.store_readings(s.dict)

    def on_snifferbuddy_status(self, status):
        """
        Log SnifferBuddy's online/offline status.

        Args:
            status (str): "Online" or "Offline"
        """
        self.logger.debug(f"-> SnifferBuddy is: {status}")


def main():
    """
    Subscribe to SnifferBuddy MQTT topics, set callback functions, and start the MQTT service.
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


if __name__ == "__main__":
    main()
