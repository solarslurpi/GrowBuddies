"""This example:

- Stores SnifferBuddy readings into an influxdb table within the database (this is explained in Gus's documentation).
- Returns a SnifferBuddy dict that contains the air readings as properties.  **including** vpd.
- Keeps the code aware of SnifferBuddy's status.
- Shows Gus's logging capability.

SnifferBuddy uses Tasmota to publish air quality readings that come in as a JSON string.  The SnifferBuddy I built publishes the following
Tasmota payload:

.. code-block:: python
   :caption: A SnifferBuddy Tasmota Payload

      tasmota_payload =  {"Time":"2022-09-06T08:52:59",
       "ANALOG":{"A0":542},
       "SCD30":{"CarbonDioxide":814,"eCO2":787,"Temperature":71.8,"Humidity":61.6,"DewPoint":57.9},"TempUnit":"F"}

Gus uses the SnifferBuddy class to convert the Tasmota payload into a SnifferBuddy dictionary.  Along with the readings provided by mqtt,
SnifferBuddy calculates the vpd and includes this measurement within the dictionary.
.. code-block:: python
   :caption: A SnifferBuddy Dictionary

       from snifferbuddy_code import SnifferBuddy
       s = SnifferBuddy(tasmota_payload)
       s.time =

def __init__(self, mqtt_dict, sensor=snifferBuddySensors.SCD30, log_level=logging.DEBUG):
.. automodule:: code.snifferbuddy_code
   :members:
   :undoc-members:
   :show-inheritance:

Gus is used to access and store the readings.  Looking at the `main()` function below, the first thing is to get an instance of Gus.


When Gus is started with the Gus.start() method, the code subscribes to SnifferBuddy's mqtt message as well as the [LWT Topic](tasmota_lwt)

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


def values_callback(snifferbuddy_dict):
    """Called by Gus when a reading from the SnifferBuddy.

    Args:
        dict (dict): identical to the dict in snifferbuddy_getreadings.py

    """
    logger.debug(f"{snifferbuddy_dict}")


def status_callback(status):
    """Identical to the status_callback function in snifferbuddy_getreadings.py

    Args:
        status (str): Either the string "Online" or "Offline".
    """
    logger.debug(f'-> SnifferBuddy is: {status}')


def main():
    """This example assumes there is a SnifferBuddy sending out readings.  We can ask Gus
        to store these readings. The following parameters are passed into Gus:
    : param SnifferBuddy_values_callback: Is set to the above values_callback() function.  When
            this parameter is set, the function passed in will be called when a new SnifferBuddy
            reading is received.  It converts the Tasmota version of the mqtt message into a SnifferBuddy
            object.
    """
    # Leaving the logging level at DEBUG and the settings file to the default name.
    snifferBuddy = Gus(SnifferBuddy_values_callback=values_callback, status_callback=status_callback,
                       snifferbuddy_table_name="sniff2")
    snifferBuddy.start()


if __name__ == "__main__":
    main()
