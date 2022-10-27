"""
This is the simplest example of interacting with the GrowBuddy devices.

"""
import logging
from ..logging_handler import LoggingHandler
from ..growbuddy_code import GrowBuddy

logger = LoggingHandler(logging.DEBUG)


def values_callback(dict):
    """Called when GrowBuddy receives a message from the SnifferBuddy.

    Args:
        dict (dict): e.g.: {'air_T': 72.5, 'RH': 58.6, 'CO2': 693, 'light_level': 264}
    """
    logger.debug(f"{dict}")


def status_callback(status):
    """Called when GrowBuddy receives an LWT message from the SnifferBuddy
    identified by the first argument passed when instantiating a GrowBuddy
    object.

    Args:
        status (str): Since these messages will come from Tasmota devices,
        The message will be either "Online" or "Offline"
    """
    logger.debug(f'-> status callback: {status}')
    # TODO: act on the device offline/online status of the device.


# Leaving the logging level at DEBUG and the settings file to the default name.
snifferbuddy = GrowBuddy("mqtt_snifferbuddy_topic", values_callback=values_callback, status_callback=status_callback)
snifferbuddy.start()
