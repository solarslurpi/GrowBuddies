"""
SnifferBuddy sends out mqtt messages that contain the air temperature, relative humidity, CO2 level, as well
as a light level readings.

**This example leverages the GrowBuddy class to return SnifferBuddy readings plus the calculated vpd value based
on the air temperature and humidity readings provided by SnifferBuddy.  If provided,
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

# Most likely you'll use DEBUG, INFO, or ERROR.
logger = LoggingHandler(logging.DEBUG)


def values_callback(dict):
    """Called when GrowBuddy receives a reading from the SnifferBuddy.

    dict (dict): e.g.:

.. code-block:: python

        dict = {'air_T': 68.2, 'RH': 59.4, 'vpd': 0.81, 'CO2': 612, 'light_level': 8}
    """
    logger.debug(f"{dict}")


def status_callback(status):
    """The status callback passed into the GrowBuddy class so we can detect
    whether the SnifferBuddy is Online or Offline.

    Args:
        status (str): Since these messages will come from Tasmota devices, The status message returned
        will be either "Online" or "Offline"
    """
    logger.debug(f'-> SnifferBuddy is: {status}')
    # TODO: act on the device offline/online status of the device.


def main():
    """First we instantiate an instance of the GrowBuddy class.  We're keeping the
    default settings file (which is code/growbuddy_settings.json).  There
    is a key "mqtt_snifferbuddy_topic".  This tells GrowBuddy to subscribe to mqtt messages
    from SnifferBuddy.  Modifiy the topic string if your topic string is different.  We pass in our
    callbacks so we can receive the values when SnifferBuddy publishes them and also SnifferBuddy's status.
    """
    # Leaving the logging level at DEBUG and the settings file to the default name.
    snifferbuddy = GrowBuddy("mqtt_snifferbuddy_topic", values_callback=values_callback, status_callback=status_callback)
    snifferbuddy.start()


if __name__ == "__main__":
    main()
