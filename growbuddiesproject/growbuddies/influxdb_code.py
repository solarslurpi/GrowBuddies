from influxdb import InfluxDBClient
from settings_code import Settings
from logginghandler import LoggingHandler


class ReadingsStore:
    def __init__(self):
        self.settings = Settings()
        self.settings.load()
        self.logger = LoggingHandler()
        self.measurement = self.settings.get("dripbuddy_table_name")
        self.hostname = self.settings.get("hostname")
        self.db_name = self.settings.get("db_name")

    def store_readings(self, tensiometer_reading, current_reading):

        # Create an InfluxDB client
        client = InfluxDBClient(host=self.hostname)
        # Select the database to use
        client.switch_database(self.db_name)
        # Set up the data in the dictionary format influxdb uses.
        data = [
            {
                "measurement": self.measurement,
                "fields": {"tensiometer": int(tensiometer_reading), "capacitive ": int(current_reading)},
            }
        ]
        # Write the data to InfluxDB
        try:
            client.write_points(data)
            self.logger.debug(
                f"successfully wrote data: **{data}** to influxdb database **{self.db_name}** table **{self.measurement}**"
            )
        except Exception as e:
            self.logger.error(f"Could not write to influx db.  Error: {e}")
