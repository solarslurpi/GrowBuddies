"""
This example Observes vpdBuddy's output.

vpdBuddy strives to maintain an ideal vpd value.  There is two ways vpdBuddy can be instantiated:

* **Observe** - A good idea to run first to get an idea on how the number of seconds vaporBuddy will be
  turned on.

* **Maintain** - A "set and forget" method.  Maintain tells vpdBuddy to maintain the ideal vpd without any
  additional intervention.
"""
from vpdbuddy_code import vpdBuddy
import logging
# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growbuddy/code')

from logging_handler import LoggingHandler

# Most likely you'll use DEBUG, INFO, or ERROR.
logger = LoggingHandler(logging.DEBUG)

def vpd_values_callback(dict):
    """_summary_

    Args:
        dict (dict): A dictionary containing vpd values for vpd, vpd setpoint,
            and the number of seconds on vpdBuddy would turn on vaporBuddy
    """
    logger.debug(f'vpd setpoint: {dict["vpd_setpoint"]}, vpd: {dict["vpd"]}seconds on: {dict["seconds_on"]}')


def main():
    vpdbuddy = vpdBuddy(vpd_values_callback=vpd_values_callback)


if __name__ == "__main__":
    main()
