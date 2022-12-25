from logginghandler import LoggingHandler
from settings_code import Settings
from mqtt_code import MQTTService
from snifferbuddyreadings_code import SnifferBuddyReadings
from mistbuddy_code import MistBuddy
import sys


class CallbacksSnifferBuddy:
    def __init__(self):
        self.logger = LoggingHandler()
        self.mistbuddy = MistBuddy()

    def on_snifferbuddy_readings(self, msg):
        s = SnifferBuddyReadings(msg)
        self.logger.debug(f"the snifferbuddy values: {s.dict}")
        self.logger.debug(f"light level is {self.mistbuddy.isLightOn(s.light_level)}")
        # vpd is most relevant when the plants are transpiring when the lights are on.
        if self.mistbuddy.isLightOn(s.light_level):
            self.mistbuddy.adjust_humidity(s)

        # The vpd value is returned. Turn on and off the humidifier based on it's value.

    def on_snifferbuddy_status(self, status):
        """`Gus()` will call this function when an `LWT` packet comes in.  `Gus()` returns a string with either
        `online` or `offline`.

        Args:
            status (str): `Gus()` sends either the string "Online" or "Offline".
        """
        self.logger.debug(f"-> snifferbuddy is: {status}")


def main():
    # Keep collecting capacitive touch readings from DripBuddy
    settings = Settings()
    settings.load()
    obj = CallbacksSnifferBuddy()
    methods = settings.get_callbacks("snifferbuddy_mqtt_dict", obj)
    mqtt_service = MQTTService(client_id="SnifferBuddy", callbacks_dict=methods)
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
