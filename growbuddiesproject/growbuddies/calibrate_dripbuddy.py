from growbuddies.logginghandler import LoggingHandler
from growbuddies.mqtt_code import MQTTService
from growbuddies.settings_code import Settings
from growbuddies.influxdb_code import ReadingsStore
import sys
import json


current_reading = None


class CallbacksDripBuddy:
    def __init__(self):
        self.logger = LoggingHandler()

    def on_dripbuddy_readings(self, msg):
        global current_reading
        mqtt_readings_dict = json.loads(msg)
        current_reading = mqtt_readings_dict["ANALOG"]["A0"]
        self.logger.debug(f"the current reading is {current_reading}")

    def on_dripbuddy_status(self, status):
        """`Gus()` will call this function when an `LWT` packet comes in.  `Gus()` returns a string with either
        `online` or `offline`.

        Args:
            status (str): `Gus()` sends either the string "Online" or "Offline".
        """
        self.logger.debug(f"-> dripBuddy is: {status}")


class CallbacksTensiometer:
    def __init__(self):
        settings = Settings()
        settings.load()
        self.table_name = settings.get("dripbuddy_table_name")
        if not self.table_name:
            raise Exception("A table name was not specified for storing the readings.")

        self.logger = LoggingHandler()

        self.readings_store = ReadingsStore()

    def on_calibrate_readings(self, tensiometer_reading):
        # Put the readings into a dictionary
        readings_dict = {"tensiometer": int(tensiometer_reading), "capacitive ": int(current_reading)}
        self.logger.debug(f"in on_calibrate_readings.  Tensiometer reading: {readings_dict} capacitive readings")
        # Store reading into influxdb table.
        self.readings_store.store_readings(self.table_name, readings_dict)


def main():
    # Keep collecting capacitive touch readings from DripBuddy
    settings = Settings()
    settings.load()
    obj = CallbacksDripBuddy()
    methods = settings.get_callbacks("dripbuddy_mqtt_dict", obj)
    mqtt_service = MQTTService(client_id="DripBuddy", callbacks_dict=methods)
    mqtt_service.start()
    obj = CallbacksTensiometer()
    methods = settings.get_callbacks("calibrate_mqtt_dict", obj)
    mqtt_service_1 = MQTTService(client_id="Tensiometer", callbacks_dict=methods)
    mqtt_service_1.start()
    while True:
        try:
            pass
        except KeyboardInterrupt:
            # Stop the MQTT service
            mqtt_service.stop()
            mqtt_service_1.stop()
            sys.exit()


if __name__ == "__main__":
    main()
