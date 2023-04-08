#
# Stores SnifferBuddy Readings into an influxdb Measurement table based on the table name set in the growbuddy_settings.json.
#
# Copyright 2023 Happy Day

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
from influxdb import InfluxDBClient
from growbuddies.settings_code import Settings
from growbuddies.logginghandler import LoggingHandler


class ReadingsStore:
    def __init__(self):
        self.settings = Settings()
        self.settings.load()
        self.logger = LoggingHandler()
        self.hostname = self.settings.get("hostname")
        self.db_name = self.settings.get("db_name")
        self.table_name = self.settings.get("snifferbuddy_table_name")

    def store_readings(self, dict_of_snifferbuddy_readings):
        if not self.table_name:
            self.logger.debug(
                "No table name is set.  Not storing readings in influxdb"
            )
            return
        # Create an InfluxDB client
        client = InfluxDBClient(host=self.hostname)
        # Select the database to use
        client.switch_database(self.db_name)
        # Set up the data in the dictionary format influxdb uses.
        data = [{"measurement": self.table_name, "fields": dict_of_snifferbuddy_readings}]
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
