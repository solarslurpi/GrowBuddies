"""
This example gets air quality readings from a snifferBuddy.

An instance of the growBuddy class returns air quality readings from snifferBuddy to a values_callback function.  The
status_callback function will be called by the growBuddy instance when there is an Offline or Online snifferBuddy event.

The example also shows Gus's logging feature.  It is an abstraction above
Python's logging, adding stack tracing as well as color coding.
The only difference between this example and the snifferbuddy_getreadings example is the storing of the
reading into an influxDB database.

The 'heavy lifter' here is Gus.


"""
import logging
# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growbuddies/code')

from logging_handler import LoggingHandler
from gus_code import Gus

# Most likely you'll use DEBUG, INFO, or ERROR.
logger = LoggingHandler(logging.DEBUG)


def values_callback(dict):
    """Called by Gus when a reading from the SnifferBuddy.

    Args:
        dict (dict): identical to the dict in snifferbuddy_getreadings.py

    """
    logger.debug(f"{dict}")


def status_callback(status):
    """Identical to the status_callback function in snifferbuddy_getreadings.py

    Args:
        status (str): Either the string "Online" or "Offline".
    """
    logger.debug(f'-> SnifferBuddy is: {status}')


def main():

    """Setting a table name is what causes growBuddy to store readings.  e.g.:

    .. code-block:: python

        db_table_name="snifferbuddy"


After this code is run, there should be entries in the influxdb database within the "snifferbuddy" measurement. e.g.::

   > select * from snifferbuddy
   name: snifferbuddy
   time                CO2 RH   air_T light_level vpd
   ----                --- --   ----- ----------- ---
   1667055876521133863 659 59.9 69.7  28          0.84
   1667055907978140667 658 59.8 69.7  17          0.84

   """
    # Leaving the logging level at DEBUG and the settings file to the default name.
    snifferBuddy = Gus(SnifferBuddy_values_callback=values_callback, status_callback=status_callback,
                       snifferbuddy_table_name="sniff2")
    snifferBuddy.start()


if __name__ == "__main__":
    main()
