import logging
from growbuddies.logginghandler import LoggingHandler
from mqtt_code import MQTTService
from settings_code import Settings
import sys
import json
from influxdb import InfluxDBClient

logger = LoggingHandler(logging.DEBUG)

current_reading = None


def store_readings(tensiometer_reading):
    settings = Settings()
    settings.load()
    measurement = settings.get('dripbuddy_table_name')

    db_name = settings.get('db_name')
    # Create an InfluxDB client
    client = InfluxDBClient(host=settings.get('hostname'))
    # Select the database to use
    client.switch_database(db_name)
    # Set up the data in the dictionary format influxdb uses.
    data = [{
        "measurement": measurement,
        "fields": {
            "tensiometer": int(tensiometer_reading),
            "capacitive ": int(current_reading)
        }
    }
    ]
    # Write the data to InfluxDB
    try:
        client.write_points(data)
        logger.debug(f'successfully wrote data: **{data}** to influxdb database **{db_name}** table **{measurement}**')
    except Exception as e:
        logger.error(f"Could not write to influx db.  Error: {e}")


class CallbacksDripBuddy:
    def on_dripbuddy_readings(self, msg):
        global current_reading
        readings_dict = json.loads(msg)
        current_reading = readings_dict["ANALOG"]["A0"]
        logger.debug(f"the current reading is {current_reading}")

    def on_dripbuddy_status(self, status):
        """`Gus()` will call this function when an `LWT` packet comes in.  `Gus()` returns a string with either
        `online` or `offline`.

        Args:
            status (str): `Gus()` sends either the string "Online" or "Offline".
        """
        logger.debug(f"-> dripBuddy is: {status}")


class CallbacksTensiometer:
    def on_calibrate_readings(self, tensiometer_reading):
        logger.debug(f"in on_calibrate_readings.  Tensiometer reading: {tensiometer_reading} capacitive reading {current_reading}")
        # Store reading into influxdb table.
        store_readings(tensiometer_reading)


def main():
    # Keep collecting capacitive touch readings from DripBuddy
    settings = Settings()
    settings.load()
    obj = CallbacksDripBuddy()
    methods = settings.get_callbacks("dripbuddy_mqtt_dict", obj)
    broker_name = settings.get("hostname")
    mqtt_service = MQTTService(client_id="DripBuddy", host=broker_name, callbacks_dict=methods)
    mqtt_service.start()
    obj = CallbacksTensiometer()
    methods = settings.get_callbacks("calibrate_mqtt_dict", obj)
    mqtt_service_1 = MQTTService(client_id="Tensiometer", host=broker_name, callbacks_dict=methods)
    mqtt_service_1.start()
    while True:
        try:
            pass
        except KeyboardInterrupt:
            # Stop the MQTT service
            mqtt_service.stop()
            mqtt_service.stop()
            sys.exit()


if __name__ == "__main__":
    main()
