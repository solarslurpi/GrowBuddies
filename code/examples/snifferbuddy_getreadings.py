"""
This example gets air quality readings from a snifferBuddy.

An instance of Gus.asdfmaskdjflsadkjf.asl returns air quality readings from snifferBuddy to a values_callback function.  The
status_callback function will be called by the growBuddy instance when there is an Offline or Online snifferBuddy event.

The example also shows the logging feature of the growBuddy class.  It is an abstraction above
Python's logging, adding stack tracing as well as color coding.

"""
import logging
# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growbuddies/code')

from logging_handler import LoggingHandler
from gus_code import Gus
from snifferbuddy_code import snifferBuddy

# Most likely you'll use DEBUG, INFO, or ERROR.
logger = LoggingHandler(logging.DEBUG)


def values_callback(snifferBuddy_values: snifferBuddy):
    """Called when Gus receives a reading from the SnifferBuddy.

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
    """Detect whether the SnifferBuddy is Online or Offline.

    Args:
        status (str): Since these messages will come from Tasmota devices, The status message returned
    will be either "Online" or "Offline"
    """
    logger.debug(f'-> SnifferBuddy is: {status}')
    # TODO: act on the device offline/online status of the device.


def test_snifferbuddy_getreadings():
    """First we instantiate an instance of the growBuddy class.  We're keeping the
    default settings file (which is code/growBuddy_settings.json).  There
    is a key "snifferbuddy_topic".  This tells growBuddy to subscribe to mqtt messages
    from SnifferBuddy.  Modifiy the topic string if your topic string is different.  We pass in our
    callbacks so we can receive the values when SnifferBuddy publishes them and also SnifferBuddy's status.
    """
    # Leaving the logging level at DEBUG and the settings file to the default name.
    snifferbuddy = Gus("snifferbuddy_topic", G=values_callback, status_callback=status_callback)
    snifferbuddy.start()


test_snifferbuddy_getreadings()
