#
# SnifferBuddyReadings takes in the air quality readings within the mqtt payload from a SnifferBuddy and converts it into a
# SnifferBuddy instance for easier and sensor agnostic access.  The SCD-30 and SCD-40 are supported sensors.
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
import math
import json


class SnifferBuddySensors:
    """These are constants containing a string identifying the air quality sensor being used."""

    SCD30 = "SCD30"
    SCD40 = "SCD40"


class SnifferBuddyConstants:
    """These are the constants representing the item id of a SnifferBuddy measurement."""

    TEMPERATURE = 0
    HUMIDITY = 1
    CO2 = 2
    LIGHT_LEVEL = 3
    TIME = 4
    VPD = 5


class SnifferBuddyReadings:
    """An instance of the "SnifferBuddyReadings" class simplifies access to data by processing the MQTT
    message payload from a SnifferBuddy device and providing properties such as the vpd, as well as a
    dictionary containing all properties. Using the raw MQTT payload may not be optimal, as it:
    - Does not include the vpd calculation.
    - Is specific to the sensor.
    - Is not as easily accessible as accessing properties directly.

    For example, the mqtt air quality message of the SCD30 is:

    .. code:: python

        {"Time":"2022-09-06T08:52:59",
         "ANALOG":{"A0":542},
         "SCD30":{"CarbonDioxide":814,"eCO2":787,"Temperature":71.8,"Humidity":61.6,"DewPoint":57.9},"TempUnit":"F"}

    Another air quality sensor may have a different message format that requires interpretation. However, the process
    of accessing properties, such as sensor readings, remains consistent and can be done in the same way as demonstrated below.


    .. code:: python

        from snifferbuddy_code import SnifferBuddyReadings
        s = SnifferBuddyReadings(mqtt)
        print({s.dict})
        print({s.vpd})


    Args:
        mqtt_payload (str): Sensor model specific mqtt message from a SnifferBuddy.
        sensor (str, optional):The constant string that identifies the air quality sensor.  The sensor must be listed in
        SnifferBuddySensors(). Defaults to SnifferBuddySensors.SCD30.
        log_level (logging level constant, optional):Logging level either logging.DEBUG, logging.INFO, logging.ERROR. Defaults to logging.DEBUG.
    """

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
            "light_level": sensor_data["light"],
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
