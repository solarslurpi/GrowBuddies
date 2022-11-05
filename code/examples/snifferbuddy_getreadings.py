"""
SnifferBuddy sends out mqtt messages that contain air quality readings.

**This example leverages the GrowBuddy class to return air quality readings from snifferBuddy.  The snifferBuddy class
figures out how to transfer the values from the sensor specific mqtt_dict to the snifferBuddy properties.
  If provided,
the status_callback function is called when an event is captured by mqtt on whether SnifferBuddy is Online or Offline.**

The example also shows the logging feature of the GrowBuddy system.  It is an abstraction above
Python's logging, adding stack tracing as well as color coding.

"""
import logging
# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growbuddy/code')

from logging_handler import LoggingHandler
from growbuddy_code import GrowBuddy
from snifferbuddy_code import snifferBuddy

# Most likely you'll use DEBUG, INFO, or ERROR.
logger = LoggingHandler(logging.DEBUG)


def values_callback(snifferBuddy_values: snifferBuddy):
    """Called when GrowBuddy receives a reading from the SnifferBuddy.

    snifferBuddy_values (snifferBuddy class): air quality values as
    properties as well as within a dictionary.

    """
    values = (f'temperature: {snifferBuddy_values.temperature},'
              f'| humidity: {snifferBuddy_values.humidity},'
              f' | co2: {snifferBuddy_values.co2},'
              f' | vpd: {snifferBuddy_values.vpd} ,'
              f' | light level: {snifferBuddy_values.light_level}')
    logger.debug(values)
    logger.debug(snifferBuddy_values.dict)


def status_callback(status):
    """The status callback passed into the GrowBuddy class so we can detect
    whether the SnifferBuddy is Online or Offline.

    Args:
        status (str): Since these messages will come from Tasmota devices, The status message returned
        will be either "Online" or "Offline"
    """
    logger.debug(f'-> SnifferBuddy is: {status}')
    # TODO: act on the device offline/online status of the device.


def test_snifferbuddy_getreadings():
    """First we instantiate an instance of the GrowBuddy class.  We're keeping the
    default settings file (which is code/growbuddy_settings.json).  There
    is a key "mqtt_snifferbuddy_topic".  This tells GrowBuddy to subscribe to mqtt messages
    from SnifferBuddy.  Modifiy the topic string if your topic string is different.  We pass in our
    callbacks so we can receive the values when SnifferBuddy publishes them and also SnifferBuddy's status.
    """
    # Leaving the logging level at DEBUG and the settings file to the default name.
    snifferbuddy = GrowBuddy("mqtt_snifferbuddy_topic", values_callback=values_callback, status_callback=status_callback)
    snifferbuddy.start()


test_snifferbuddy_getreadings()