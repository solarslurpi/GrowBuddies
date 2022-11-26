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


from mistbuddy_code import mistBuddy
import logging
from logginghandler import LoggingHandler


# Most likely you'll use DEBUG, INFO, or ERROR.
logger = LoggingHandler(logging.DEBUG)


def mistBuddy_values_callback(setpoint: float, vpd: float, nSecondsON: int, error: float) -> None:
    """mistBuddy() calls this function when it has updated vpd values on how
    many seconds to turn mistBuddy on.

    """
    global mistBuddy

    # Write the vpd values to log as info.
    values = (f'vpd setpoint: {setpoint}'
              f'| vpd value: {vpd}'
              f' | n seconds to turn on mistBuddy: {nSecondsON}',
              f' | error value: {error}')
    logger.info(values)
    # Store number of seconds to turn on mistBuddy in influxdb.
    try:
        fields = {"vpd": vpd,
                  "setpoint": setpoint,
                  "error": error,
                  "seconds_on": nSecondsON,
                  "error": error
                  }
        mistBuddy.db_write("vpdBuddy_40_01_01_error_eval_1", fields)
    except Exception as e:
        logger.error(f"Error!  Could not write to to the vpdBuddy table in influxdb.  Error: {e}")


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
    global mistBuddy
    mistbuddy = mistBuddy(vpd_values_callback=mistBuddy_values_callback, manage=True)

    mistbuddy.start()


if __name__ == "__main__":
    main()
