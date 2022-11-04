
import logging
from logging_handler import LoggingHandler
from util_code import calc_vpd


class snifferBuddySensors:
    """An enumeration to let GrowBuddy know if the plants it is caring for are in the vegetative or flower growth stage.
    This class is used internally to make it easy to follow if the running code assumes the Vegetative or Flower state.

    Args:
        Enum (int): Either VEG for Vegetative of FLOWER for when the plant is in flowering.

    """
    SCD30 = "SCD30"


class snifferBuddyConstants:
    TEMPERATURE = 0
    HUMIDITY = 1
    CO2 = 2
    LIGHT_LEVEL = 3
    # Note: vpd is a function of temperature and humidity.


class snifferBuddy():

    def __init__(self, mqtt_dict, sensor=snifferBuddySensors.SCD30, log_level=logging.DEBUG):
        self.sensor = sensor
        self.mqtt_dict = mqtt_dict
        # self.temperature = property(self._get_temperature, self._set_temperature)
        # No entry for vpd because vpd is a calculated value based on
        # temperature and humidity.
        self.name_dict = {snifferBuddySensors.SCD30: ["Temperature", "Humidity", "CarbonDioxide", "light_level"]
                          }
        # Set up logging.  LoggingHandler gives stack trace information.
        self.logger = LoggingHandler(log_level)
        self.logger.debug(
            "-> Initializing snifferBuddy class."
        )

    def _get_item(self, item_number: int):
        try:
            item_name = self.name_dict[self.sensor][item_number]
            item = None
            # e.g. for temperature:
            # temperature = item = mqtt_dict["SCD30"]["Temperature"]
            if self.sensor == snifferBuddySensors.SCD30: 
                if item_number == snifferBuddyConstants.LIGHT_LEVEL:
                    # Light level is part of Snifferbuddy, but not the SCD30.
                    item = self.mqtt_dict["ANALOG"]["A0"]
                else:
                    item = self.mqtt_dict[self.sensor][item_name]
        except Exception as e:
            self.logger.error(f"Could not get item for {self.sensor} item number {item_number}.  Error: {e}. There should be an entry in name_dict.")
        return item

    @property
    def temperature(self) -> float:
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
