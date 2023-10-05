#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
from influxdb import InfluxDBClient
from growbuddies.settings_code import Settings
from growbuddies.logginghandler import LoggingHandler


class ReadingsStore:
    def __init__(self, table_name=None):
        self.settings = Settings()
        self.settings.load()
        self.logger = LoggingHandler()
        # By default this code assumes the standard snifferbuddy readings...
        # But for example in MistBuddy a table of readings can be created for
        # tuning purposes.
        self.hostname = self.settings.get("hostname")
        self.db_name = self.settings.get("db_name")
        if table_name:
            self.table_name = table_name
        else:
            self.table_name = self.settings.get("snifferbuddy_table_name")

    def store_readings(self, dict):
        if not self.table_name:
            self.logger.debug("No table name is set.  Not storing readings in influxdb")
            return
        # Create an InfluxDB client
        client = InfluxDBClient(host=self.hostname)
        # Select the database to use
        client.switch_database(self.db_name)
        # Set up the data in the dictionary format influxdb uses.
        data = [{"measurement": self.table_name, "fields": dict}]
        # Write the data to InfluxDB
        try:
            client.write_points(data)
            self.logger.debug(
                f"successfully wrote data: **{data}** to influxdb database **{self.db_name}** table **{self.table_name}**"
            )
        except Exception as e:
            self.logger.error(
                f"Could not write to influx db.  **{data}** to influxdb database **{self.db_name}** table **{self.table_name}** Error: {e}"
            )
