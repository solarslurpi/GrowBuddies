from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings
from growbuddies.mqtt_code import MQTTService
from growbuddies.snifferbuddyreadings_code import SnifferBuddyReadings
from growbuddies.mistbuddy_code import MistBuddy
from growbuddies.influxdb_code import ReadingsStore
import sys


class CallbacksSnifferBuddy:
    def __init__(self):
        self.logger = LoggingHandler()
        self.mistbuddy = MistBuddy()
        settings = Settings()
        settings.load()
        self.table_name = settings.get("snifferbuddy_table_name")
        self.readings_store = ReadingsStore()

    def on_snifferbuddy_readings(self, msg):
        # Translate the mqtt message into a SnifferBuddy class.
        s = SnifferBuddyReadings(msg)
        self.logger.debug(f"the snifferbuddy values: {s.dict}")
        on_or_off_str = "ON" if self.mistbuddy.isLightOn(s.light_level) else "OFF"
        self.logger.debug(f"The light is {on_or_off_str}")
        # Adjust vpd. vpd is most relevant when the plants are transpiring when the lights are on.
        if self.mistbuddy.isLightOn(s.light_level):
            self.mistbuddy.adjust_humidity(s)
        # Store readings
        if self.table_name:
            self.readings_store.store_readings(s.dict)

    # The vpd value is returned. Turn on and off the humidifier based on it's value.

    def on_snifferbuddy_status(self, status):
        """`Gus()` will call this function when an `LWT` packet comes in.  `Gus()` returns a string with either
        `online` or `offline`.

        Args:
            status (str): `Gus()` sends either the string "Online" or "Offline".
        """
        self.logger.debug(f"-> snifferbuddy is: {status}")
        # TODO: send alert if offline since snifferbuddy readings are the heartbeat.


def main():
    # Keep collecting capacitive touch readings from DripBuddy
    settings = Settings()
    settings.load()
    obj = CallbacksSnifferBuddy()
    methods = settings.get_callbacks("snifferbuddy_mqtt_dict", obj)
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
