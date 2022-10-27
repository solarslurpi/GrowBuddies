
import logging

from logging_handler import LoggingHandler
from growbuddy_code import GrowBuddy

logger = LoggingHandler(logging.DEBUG)


def values_callback(dict):
    logger.debug(f"{dict}")


def status_callback(status):
    logger.debug(f'-> status callback: {status}')
    pass


# Leaving the logging level at DEBUG and the settings file to the default name.
snifferbuddy = GrowBuddy("mqtt_snifferbuddy_topic", values_callback=values_callback, status_callback=status_callback)
snifferbuddy.start()
