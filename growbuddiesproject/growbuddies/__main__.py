"""
=============================
Storing SnifferBuddy Readings
=============================
Now that you have set up a SnifferBuddy device that is sending readings through MQTT messages, and you have an MQTT broker (Gus) in place to route those messages, it is time to store the data for post visualization.

This Python script stores SnifferBuddyReadings - including the vpd value - into an influxdb measurement table.

The script can be run from the command line (within you virtual environment) by typing `store-readings`.


This script performs the following tasks:

1. Subscribes to mqtt messages from SnifferBuddy. See the :meth:`main` method.
2. When a SnifferBuddy message is received, it calculates the vpd (vapor pressure deficit).
3. Stores the SnifferBuddy reading and the calculated vpd value in an influxdb database.
4. Logs debug messages for easier debugging.


"""
from growbuddies.mqtt_code import MQTTService
from growbuddies.settings_code import Settings
from growbuddies.snifferbuddyreadings_code import SnifferBuddyReadings
from growbuddies.logginghandler import LoggingHandler
import sys


class Callbacks:
    def __init__(self):
        self.logger = LoggingHandler()

    def on_snifferbuddy_readings(self, s: SnifferBuddyReadings):

        """SnifferBuddy uses Tasmota to publish air quality readings that come in as a JSON string.  A SnifferBuddy built with an SCD30 sensor will send out messages with payloads similar to:

        .. code-block:: json

            {
                "Time": "2022-11-24T13:12:37",
                "ANALOG": {"A0": 1024},
                "SCD30": {
                    "CarbonDioxide": 630,
                    "eCO2": 661,
                    "Temperature": 73.3,
                    "Humidity": 50.0,
                    "DewPoint": 53.5
                },
                "TempUnit": "F"
            }


        Before the readings are received by this callback, they are transformed into a sensor agnostic Python class, SnifferBuddyReadings().

        .. code-block:: python

           s = SnifferBuddyReadings(tasmota_payload)
                    print(f"Time: {s.time}, Temperature (F): {s.temp}, Humidity: {s.humidity})
                    s.time = "2022-09-06T08:52:59"
                    s.temperature = 71.8
                    s.humidity = 61.6
                    s.co2 = 814
                    s.light_level = 542
                    s.vpd = 1.23

        The above example shows how easy it is to get individual values.  Alternatively, `s.dict` returns a dictionary containing all of the values.

        """
        self.logger.debug(f"{s.dict}")

    def on_snifferbuddy_status(self, status):
        """

        .. note::
        How SnifferBuddy's status is determined is discussed in :ref:`mqtt_LWT`.


        If the `status_callback` parameter is set to a function, `Gus()` will call the function when an `LWT` packet comes in.
        `Gus()` returns a string with either `online` or `offline`.

        Args:
            status (str): `Gus()` sends either the string "Online" or "Offline".
        """
        self.logger.debug(f"-> SnifferBuddy is: {status}")


def main():
    """The goal of this script is to store the SnifferBuddy readings along with the calculated vpd value in a measurement table within InfluxDB.
    To achieve this goal, the script defines two callback functions:
    one for handling SnifferBuddy readings and the other for handling status information.



    The Settings class reads in parameters used by the GrowBuddies from the `growbuddy_settings.json <https://github.com/solarslurpi/GrowBuddies/blob/main/growbuddiesproject/growbuddies/growbuddies_settings.json>`_ file. One of these parameters is a dictionary
    containing information for subscribing to SnifferBuddy's MQTT topics. The MQTTService class uses this dictionary to determine which callback
    function to use when it receives a message. Specifically, it will use the readings callback if the message contains air readings, or the status
    callback if the message contains SnifferBuddy status information such as "online" or "offline".

    .. code-block:: json

        "snifferbuddy_mqtt_dict":
                                    {"tele/snifferbuddy/SENSOR": "on_snifferbuddy_readings",
                                     "tele/snifferbuddy/LWT": "on_snifferbuddy_status"},


    The above is the default entry.  The topic is the dictionary's key.  The name of the callback function is the value.  Notice this script includes the two
    methods :meth:`Callbacks.on_snifferbuddy_readings` and :meth:`Callbacks.on_snifferbuddy_status`.

    """
    settings = Settings()
    settings.load()
    # Create an MQTTService instance
    obj = Callbacks()
    methods = settings.get_callbacks("snifferbuddy_mqtt_dict", obj)
    mqtt_service = MQTTService(client_id="SnifferBuddy", callbacks_dict=methods)
    mqtt_service.start()
    while True:
        try:
            pass
        except KeyboardInterrupt:
            # Stop the MQTT service
            mqtt_service.stop()
            sys.exit()


if __name__ == "__main__":
    main()
