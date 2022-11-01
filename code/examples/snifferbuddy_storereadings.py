"""

**The only difference between this example and the**

`snifferbuddy_getreadings <https://tinyurl.com/mrxwhc6z>`_

**example is the storing of the reading into an influxDB database**

The 'heavy lifter' here is the GrowBuddy class.

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
    """Called by GrowBuddy when the instance receives a reading from the SnifferBuddy.

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
    # TODO: act on the device offline/online status of the device.


def main():

    """The difference in instantiating an instance of GrowBuddy as just reading versus storing
        readings is including a name of a table (aka measurement in influxdb lingo) where the results
        will be stored.  e.g.:
.. code-block:: python

   db_table_name="snifferbuddy"


After this code is run, there should be entries in the database within the "snifferbuddy" measurement. e.g.::

   > select * from snifferbuddy
   name: snifferbuddy
   time                CO2 RH   air_T light_level vpd
   ----                --- --   ----- ----------- ---
   1667055876521133863 659 59.9 69.7  28          0.84
   1667055907978140667 658 59.8 69.7  17          0.84

   """
    # Leaving the logging level at DEBUG and the settings file to the default name.
    snifferbuddy = GrowBuddy("mqtt_snifferbuddy_topic", values_callback=values_callback, status_callback=status_callback,
                             db_table_name="snifferbuddy")
    snifferbuddy.start()


if __name__ == "__main__":
    main()
