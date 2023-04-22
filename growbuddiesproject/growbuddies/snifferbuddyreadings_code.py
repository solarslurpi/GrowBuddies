#
# SnifferBuddyReadings takes in the air quality readings within the mqtt payload from a SnifferBuddy and converts it into a
# SnifferBuddy instance for easier and sensor agnostic access.  The SCD-30 and SCD-4X are supported sensors.
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
from growbuddies.logginghandler import LoggingHandler
import json


class SnifferBuddyReadings:
    def __init__(self, mqtt_payload):
        # Set up logging.  LoggingHandler gives stack trace information.
        self.logger = LoggingHandler()
        self.logger.debug("-> Initializing SnifferBuddy class.")
        self.valid_packet = True

        self.mqtt_payload = json.loads(mqtt_payload)
        # The air quality sensor's name in the mqtt message. If it isn't there, we assume
        # This payload is not from a SnifferBuddy.
        try:
            self.sensor_name = self._find_sensor_name_in_payload()
        except Exception as e:
            self.logger.error(f"Could not identify the air quality sensor.  Error: {e}")
            self.valid_packet = False
        self.dict = self._make_dict()

    def _find_sensor_name_in_payload(self) -> str:
        sensor_names_known_set = set(["scd30", "scd40", "scd41"])
        sensor_name_in_mqtt = next(iter(self.mqtt_payload))
        if sensor_name_in_mqtt in sensor_names_known_set:
            return sensor_name_in_mqtt
        else:
            # Create a comma-separated string of the sensor names
            sensor_names_str = ", ".join(sensor_names_known_set)
            raise NameError(f"Could not find a valid sensor. Current valid sensors include {sensor_names_str}")

    def _make_dict(self) -> dict:
        # At this point, I made this specific to the SnifferBuddy I built.  This way, I won't overcomplicate,
        sensor_data = self.mqtt_payload[self.sensor_name]
        return {
            "temperature": sensor_data["temperature"],
            "humidity": sensor_data["humidity"],
            "co2": sensor_data["co2"],
            "vpd": sensor_data["vpd"],
            "light": sensor_data["light"],
        }

    @property
    def temperature(self) -> float:
        return self.dict["temperature"]

    @property
    def humidity(self) -> float:
        return self.dict["humidity"]

    @property
    def co2(self) -> float:
        return self.dict["co2"]

    @property
    def vpd(self) -> float:
        return self.dict["vpd"]

    @property
    def light_level(self) -> str:
        return self.dict["light"]
