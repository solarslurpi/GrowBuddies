"""
This example Observes vpdBuddy's output.

vpdBuddy strives to maintain an ideal vpd value.  There is two ways vpdBuddy can be instantiated:

* **Observe** - A good idea to run first to get an idea on how the number of seconds vaporBuddy will be
  turned on.

* **Maintain** - A "set and forget" method.  Maintain tells vpdBuddy to maintain the ideal vpd without any
  additional intervention.
"""
# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growbuddy/code')

from vpdbuddy_code import vpdBuddy
import logging


from logging_handler import LoggingHandler

# Most likely you'll use DEBUG, INFO, or ERROR.
logger = LoggingHandler(logging.DEBUG)


def vpd_values_callback(dict):
    """Called back by vpdBuddy if the vpd_values_callback is set.  This way we
    can observe the values vpdBuddy calculates.

    Args:
        dict (dict): A dictionary containing vpd values for vpd, vpd setpoint,
            and the number of seconds on vpdBuddy would turn on vaporBuddy.
    """
    logger.debug(f'vpd setpoint: {dict["vpd_setpoint"]}, vpd: {dict["vpd"]}seconds on: {dict["seconds_on"]}')


def main():
    """vpdBuddy() inherits from growBuddy().  Thus, all the parameters that
    can be passed into instantiating an instance of growBuddy() can
    be used here.  In addition, vpBuddy has it's own parameters. We set the
    callback function and leave other parameters to their default.  In particular,
    the manage parameter defaults to False.  Which is what we want.
    """

    vpdbuddy = vpdBuddy(vpd_values_callback=vpd_values_callback)
    vpdbuddy.start()


if __name__ == "__main__":
    main()
