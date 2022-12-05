
"""
========
Overview
========
This example:

- Returns SnifferBuddy readings **including** vpd.
- Stores SnifferBuddy readings into an influxdb table within the database.
- Keeps the code aware of SnifferBuddy's status.
- Shows `Gus()`'s logging capability.

============================
Return SnifferBuddy Readings
============================
SnifferBuddy uses Tasmota to publish air quality readings that come in as a JSON string.  The SnifferBuddy I built publishes the following
Tasmota payload:

.. code-block:: python
   :caption: A SnifferBuddy Tasmota Payload

      tasmota_payload =  "Time":"2022-11-24T13:12:37",
       "ANALOG":{"A0":1024},
       "SCD30":{"CarbonDioxide":630,"eCO2":661,"Temperature":73.3,"Humidity":50.0,"DewPoint":53.5},"TempUnit":"F"}

`Gus()` uses the `SnifferBuddyReadings()` class to convert the Tasmota payload into easily accessible variables.  If `Gus()` is
passed in a `SnifferBuddyReadings_callback` function when initialized, the values will be returned within a `SnifferBuddyReadings` instance.

.. code-block:: python
   :caption: Accessing SnifferBuddy Readings

       from snifferbuddy_code import SnifferBuddyReadings

       def snifferbuddyreadings(snifferBuddyReadings):
       s = SnifferBuddyReadings(tasmota_payload)
            print(f"Time: {s.time}, Temperature (F): {s.temp}, Humidity: {s.humidity})
            s.time = "2022-09-06T08:52:59"
            s.temperature = 71.8
            s.humidity = 61.6
            s.co2 = 814
            s.light_level = 542
            s.vpd = 1.23


============================
Store SnifferBuddy Readings
============================

.. note::
   This example assumes you have installed influxdb and created the `gus` database as noted in `Gus()`'s page under :ref:`influxdb_install`.

The table name is set to "sniff2" in `main()`
(`SnifferBuddyReadings_table_name="sniff2"`).

==========================
Get SnifferBuddy's Status
==========================

.. note::
   How SnifferBuddy's status is determined is discussed in :ref:`mqtt_LWT`.


If the `status_callback` parameter is set to a function, `Gus()` will call the function when an `LWT` packet comes in.
`Gus()` returns a string with either `online` or `offline`.

Functions
~~~~~~~~~
"""
import logging

from growbuddies.logginghandler import LoggingHandler
from growbuddies.gus import Gus

# # Most likely you'll use DEBUG, INFO, or ERROR.
logger = LoggingHandler(logging.DEBUG)


def snifferbuddyreadings(snifferBuddyReadings):
    """This is the `SnifferBuddyReadings_callback` function that was set when an instance of `Gus()`
    was initialized in `main()`.
    The air quality values will find their way to this callback function when an instance of `Gus()` is initialized with:

    Args:
        snifferBuddyReadings (SnifferBuddyReadings): An instance of SnifferBuddyReadings.

    """
    logger.debug(f"{snifferBuddyReadings.dict}")


def status_callback(status):
    """`Gus()` will call this function when an `LWT` packet comes in.  `Gus()` returns a string with either
    `online` or `offline`.

    Args:
        status (str): `Gus()` sends either the string "Online" or "Offline".
    """
    logger.debug(f'-> SnifferBuddy is: {status}')


def main():
    """We initialize an instance of `Gus()` with the following parameters.  The defaults are fine for
    the other parameters.

    Args:


        SnifferBuddyReadings_callback (function, optional): Function called by `Gus()` to return an instance of a SnifferBuddyReadings().

        status_callback (function, optional): Function called by `Gus()` when an LWT message is received. The `status_callback` function receives
            a string containing either `online` or `offline`.

        SnifferBuddyReadings_table_name (str, optional): Name of measurement table in influxdb that stores snifferBuddy readings.


    After getting an instance of `Gus()` with these parameters, Call the `start()` method.

    """
    table_name = input("Enter the table name where SnifferBuddyReadings will be Stored (Default is SnifferBuddyReadings): ")
    if not table_name or table_name == "":
        table_name = "SnifferBuddyReadings"
    # Leaving the logging level at DEBUG and the settings file to the default name.
    snifferBuddyReadingsInstance = Gus(SnifferBuddyReadings_callback=snifferbuddyreadings, status_callback=status_callback,
                                       SnifferBuddyReadings_table_name= table_name)
    snifferBuddyReadingsInstance.start()


if __name__ == "__main__":
    main()
