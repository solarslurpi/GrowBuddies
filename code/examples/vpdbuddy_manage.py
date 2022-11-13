"""
This example uses vpdBuddy to turn on and off mistBuddy in order to most efficiently maintain the ideal vpd value.

vpdBuddy strives to maintain an ideal vpd value.  There is two ways vpdBuddy can be instantiated:

* **Observe** - A good idea to run first to get an idea on how the number of seconds mistBuddy will be
  turned on.

* **Maintain** - A "set and forget" method.  Maintain tells vpdBuddy to maintain the ideal vpd without any
  additional intervention.

* ** This example Observes. **
"""
# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growbuddy/code')


from vpdbuddy_code import vpdBuddy
import logging


from logging_handler import LoggingHandler


# Most likely you'll use DEBUG, INFO, or ERROR.
logger = LoggingHandler(logging.DEBUG)


def vpd_values_callback(setpoint: float, vpd: float, nSecondsON: int) -> None:
    """vpdBuddy() calls this function when it has updated vpd values on how
    many seconds to turn mistBuddy on.

    """
    values = (f'vpd setpoint: {setpoint}'
              f'| vpd value: {vpd}'
              f' | n seconds to turn on mistBuddy: {nSecondsON}')
    logger.info(values)


def main():
    """vpdBuddy() inherits from growBuddy().  Thus, all the parameters that
    can be passed into instantiating an instance of growBuddy() can
    be used here.  In addition, vpBuddy has it's own parameters. We set the
    callback function and leave other parameters to their default.  In particular,
    the manage parameter defaults to False.  Which is what we want.
    """
    # To store snifferBuddy readings into the database, set the parameter
    # snifferbuddy_table_name.
    # To store the date/time vpdBuddy turned mistBuddy ON and OFF, set the
    # parameter vpdbuddy_table_name.
    vpdbuddy = vpdBuddy(vpd_values_callback=vpd_values_callback, manage=True, snifferbuddy_table_name="snifferbuddy_run2")
    vpdbuddy.start()


if __name__ == "__main__":
    main()
