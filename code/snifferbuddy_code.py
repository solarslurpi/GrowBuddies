
import logging
from logging_handler import LoggingHandler
from util_code import calc_vpd


class snifferBuddySensors:
    """These are constants containing a string identifying the air quality sensor being used.
    Starting off, only the SCD30 is available.

    """
    SCD30 = "SCD30"


class snifferBuddyConstants:
    """These are the constants representing the item id of a SnifferBuddy measurement.  It is used for mapping between
    The mqtt message and the snifferBuddy property.
    """
    TEMPERATURE = 0
    HUMIDITY = 1
    CO2 = 2
    LIGHT_LEVEL = 3
    # Note: vpd is a function of temperature and humidity.


class snifferBuddy():
    """The snifferBuddy class takes in the mqtt packet sent by the snifferBuddy and then transfer the
    values to the snifferBuddy properties itemized below.

    For example, the payload of the SCD30 mqtt message is:

    .. code:: python

        {"Time":"2022-09-06T08:52:59",
         "ANALOG":{"A0":542},
         "SCD30":{"CarbonDioxide":814,"eCO2":787,"Temperature":71.8,"Humidity":61.6,"DewPoint":57.9},"TempUnit":"F"}

    Another air quality sensor will have a different message that needs to be understood.  The snifferBuddy class takes
    in the sensor specific mqtt message and transfers the values for Temperature, Humidity, CO2, and light level.  Instead
    of access the mqtt message, Buddies access the properties of an instance of the snifferBuddy class.

    Args:
        mqtt_dict (dict): Sensor model specific mqtt message from a snifferBuddy.
        sensor (str, optional):The constant string that identifies the air quality sensor.  The sensor must be listed in
        snifferBuddySensors(). Defaults to snifferBuddySensors.SCD30.
        log_level (logging level constant, optional):Logging level either logging.DEBUG, logging.INFO, logging.ERROR. Defaults to logging.DEBUG.
    """

    def __init__(self, mqtt_dict, sensor=snifferBuddySensors.SCD30, log_level=logging.DEBUG):

        self.sensor = sensor
        self.mqtt_dict = mqtt_dict
        # The air quality sensor's names in the mqtt message.
        self.name_dict = {snifferBuddySensors.SCD30: ["Temperature", "Humidity", "CarbonDioxide"]
                          }
        # Set up logging.  LoggingHandler gives stack trace information.
        self.logger = LoggingHandler(log_level)
        self.logger.debug(
            "-> Initializing snifferBuddy class."
        )

    def _get_item(self, item_number: int):
        try:

            item = None
            # e.g. for temperature:
            # temperature = item = mqtt_dict["SCD30"]["Temperature"].  If the item is for
            # the temperature, the item_number is 0.
            if self.sensor == snifferBuddySensors.SCD30:
                if item_number == snifferBuddyConstants.LIGHT_LEVEL:
                    # Light level is part of Snifferbuddy, but not the SCD30.
                    item = self.mqtt_dict["ANALOG"]["A0"]
                else:
                    item_name = self.name_dict[self.sensor][item_number]
                    item = self.mqtt_dict[self.sensor][item_name]
        except Exception as e:
            self.logger.error(f"Could not get item for {self.sensor} item number {item_number}.  Error: {e}. There should be an entry in name_dict.")
        return item

    @property
    def dict(self) -> dict:
        return {"temperature": self.temperature,
                "humidity": self.humidity,
                "co2": self.co2,
                "vpd": self.vpd,
                "light_level": self.light_level}

    @property
    def temperature(self) -> float:
        # I set the temperature to F.
        t = self._get_item(snifferBuddyConstants.TEMPERATURE)
        return t

    @property
    def humidity(self) -> float:
        h = self._get_item(snifferBuddyConstants.HUMIDITY)
        return h

    @property
    def co2(self) -> float:
        c = self._get_item(snifferBuddyConstants.CO2)
        return c

    @property
    def vpd(self) -> float:
        h = self._get_item(snifferBuddyConstants.HUMIDITY)
        t = self._get_item(snifferBuddyConstants.TEMPERATURE)
        v = calc_vpd(t, h)
        return v

    @property
    def light_level(self) -> int:
        ll = self._get_item(snifferBuddyConstants.LIGHT_LEVEL)
        return ll
