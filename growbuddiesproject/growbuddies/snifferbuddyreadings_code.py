#
# SnifferBuddyReadings takes in the air quality readings within the mqtt payload from a SnifferBuddy and converts it into a SnifferBuddy instance
# for easier and sensor agnostic access.  The SCD-30 and SCD-40 are supported sensors.
#
# Copyright 2022 Happy Day

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
    # Note: vpd is not listed because it is a function of temperature and humidity.


class SnifferBuddyReadings:
    """Takes in an mqtt air quality message from a SnifferBuddy and translates into an easy to use set of properties.

    The mqtt air quality message is sensor specific different.  Different air quality sensors will have a different message format.

    For example, the mqtt air quality message of the SCD30 is:

    .. code:: python

        {"Time":"2022-09-06T08:52:59",
         "ANALOG":{"A0":542},
         "SCD30":{"CarbonDioxide":814,"eCO2":787,"Temperature":71.8,"Humidity":61.6,"DewPoint":57.9},"TempUnit":"F"}

    Another air quality sensor will have a different message that needs to be understood.


    .. code:: python

        from snifferbuddy_code import SnifferBuddyReadings
        s = SnifferBuddyReadings(mqtt_dict)
        print({s.dict})
        print({s.vpd})


    Args:
        mqtt_dict (dict): Sensor model specific mqtt message from a SnifferBuddy.
        sensor (str, optional):The constant string that identifies the air quality sensor.  The sensor must be listed in
        SnifferBuddySensors(). Defaults to SnifferBuddySensors.SCD30.
        log_level (logging level constant, optional):Logging level either logging.DEBUG, logging.INFO, logging.ERROR. Defaults to logging.DEBUG.
    """

    def __init__(self, mqtt_str):

        # Set up logging.  LoggingHandler gives stack trace information.
        self.logger = LoggingHandler()
        self.logger.debug("-> Initializing SnifferBuddy class.")

        self.mqtt_dict = json.loads(mqtt_str)
        # The air quality sensor's name in the mqtt message.
        try:
            self.sensor = self._find_sensor_name(self.mqtt_dict)
            self.name_dict = {self.sensor: ["Temperature", "Humidity", "CarbonDioxide"]}
        except Exception as e:
            self.logger.error(f"Could not identify the air quality sensor. Error: {e}")

    def _find_sensor_name(self, mqtt_dict):
        sensor_names = ["SCD30", "SCD40"]
        for item in sensor_names:
            for key in mqtt_dict.items():
                if item in key:
                    return item
        raise NameError("Could not find a valid sensor. Current valid sensors include the SCD30 and SCD40")

    def _get_item(self, item_number: int):
        try:

            item = None
            # e.g. for temperature:
            # temperature = item = mqtt_dict["SCD30"]["Temperature"].  If the item is for
            # the temperature, the item_number is 0.
            if item_number == SnifferBuddyConstants.TIME:
                item = self.mqtt_dict["Time"]
                return item
            if self.sensor == SnifferBuddySensors.SCD30 or self.sensor == SnifferBuddySensors.SCD40:
                if item_number == SnifferBuddyConstants.LIGHT_LEVEL:
                    # Light level is part of SnifferBuddy, but not the SCD30.
                    item = self.mqtt_dict["ANALOG"]["A0"]
                else:
                    item_name = self.name_dict[self.sensor][item_number]
                    item = self.mqtt_dict[self.sensor][item_name]
        except Exception as e:
            self.logger.error(
                f"Could not get item for {self.sensor} item number {item_number}.  Error: {e}. There should be an entry in name_dict."
            )
        return item

    def _calc_vpd(self, temperature: float, humidity: float) -> (float):

        """INTERNAL METHOD. I decided at this point not to measure the leaf temperature but take the much simpler
        approach of assuming 2 degrees F less than the air temperature.  Clearly not as accurate as reading.  But for
        my purposes "good enough."

        Once an mqtt message is received from the growBuddy broker that a SnifferBuddy reading is available, _calc_vpd()
        is called to calculate the VPD.  The mqtt message comes in as a JSON string.  The JSON string is converted to a
        dictionary.  The dictionary contains the values needed for the VPD calculation.

        The VPD equation comes
        `from a Quest website <https://www.questclimate.com/vapor-pressure-deficit-indoor-growing-part-3-different-stages-vpd/>`_

        Args:
            dict (dict): Dictionary of values returned from an mqtt message.
        Raises:
            Exception: If one of the values needed to calculate the VPD is of a type or value that won't work.

        Returns the calculated VPD value.
        """
        # TODO: Make usable for at least the SCD30 or SCD40
        air_T = temperature
        RH = humidity
        if not isinstance(air_T, float) or not isinstance(RH, float) or air_T <= 0.0 or RH <= 0.0:
            raise Exception(
                f"Received unexpected values for either the temperature ({air_T}) or humidity ({RH}) or both"
            )
        leaf_T = air_T - 2
        vpd = 3.386 * (
            math.exp(17.863 - 9621 / (leaf_T + 460)) - ((RH / 100) * math.exp(17.863 - 9621 / (air_T + 460)))
        )
        return round(vpd, 2)

    @property
    def dict(self) -> dict:
        """Returns SnifferBuddy readings as a dictionary.

        Returns:
            dict: Contains values for temperature, humidity, co2, vpd, and light level.

        We're not returning the time.  When we store the variables, influxdb adds a timestamp.
        """
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "co2": self.co2,
            "vpd": self.vpd,
            "light_level": self.light_level,
        }

    @property
    def temperature(self) -> float:
        """Return SnifferBuddy's temperature reading

        Returns:
            float: SnifferBuddy's reading of the air temperature.  Whether it is in F or C is dependent on how you set up SnifferBuddy.
        """
        # I set the temperature to F.
        t = self._get_item(SnifferBuddyConstants.TEMPERATURE)
        return t

    @property
    def time(self) -> str:
        """Returns a string containing the date and time that can be converted into a datetime."""
        time = self._get_item(SnifferBuddyConstants.TIME)
        return time

    @property
    def humidity(self) -> float:
        h = self._get_item(SnifferBuddyConstants.HUMIDITY)
        return h

    @property
    def co2(self) -> float:
        c = self._get_item(SnifferBuddyConstants.CO2)
        return c

    @property
    def vpd(self) -> float:
        h = self._get_item(SnifferBuddyConstants.HUMIDITY)
        t = self._get_item(SnifferBuddyConstants.TEMPERATURE)
        v = self._calc_vpd(t, h)
        return v

    @property
    def light_level(self) -> int:
        ll = self._get_item(SnifferBuddyConstants.LIGHT_LEVEL)
        return ll
