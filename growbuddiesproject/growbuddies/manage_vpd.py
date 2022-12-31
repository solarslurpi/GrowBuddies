"""
manage_vpd.py
=============

This script utilizes MistBuddy to regulate the operation of the humidifier,
turning it on and off as necessary to maintain the optimal vapor pressure deficit (VPD) level.
The `main()` function initiates the program by establishing callback functions and subscribing to SnifferBuddy
readings through the :py:class:`growbuddies.mqtt_code.MQTTService` class. When a reading is received, the `on_snifferbuddy_readings` callback activates
the `MistBuddy()` class to turn on the humidifier if the vapor pressure deficit (VPD) value exceeds the ideal range
determined by the VPD chart.

       .. image:: ../docs/images/vpd_chart.jpg
            :scale: 50
            :alt: Flu's vpd chart
            :align: center

The growbuddy_settings.json file contains several parameters that are used as input for the program.

    .. code-block:: json

        "vpd_growth_stage": "veg",
        "vpd_setpoints": {
            "veg": 0.9,
            "flower": 1.0
        },


vpd_growth_stage : Lets MistBuddy know what growth stage the plants are in.  There are two stages:
    - "veg" for vegetative.
    - "flower" For the flowering stage.

The above settings are using by the MistBuddy code, see :py:meth:`Callbacks.on_snifferbuddy_readings`  dictate the behavior of MistBuddy for this specific run. The plants are currently in the vegetative growth stage.
Based on the VPD chart, the ideal VPD value for this stage is 0.9. Therefore, MistBuddy will use 0.9 as the setpoint value in
order to maintain optimal conditions for the plants during this stage of growth.
growbuddiesproject/growbuddies/PID_code.py


The two SnifferBuddy callbacks are sent to the MQTTService():

    .. code-block:: json

        "snifferbuddy_mqtt_dict": {"tele/snifferbuddy/SENSOR": "on_snifferbuddy_readings",
                          "tele/snifferbuddy/LWT": "on_snifferbuddy_status"},

by passing in the "snifferbuddy_mqtt_dict" keyword, the MQTTService() knows which callback goes with which MQTT topic, making it easy to
subscribe to the topic and then callback the callback functions when a message is received.

"""
from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings
from growbuddies.mqtt_code import MQTTService
from growbuddies.snifferbuddyreadings_code import SnifferBuddyReadings
from growbuddies.mistbuddy_code import MistBuddy
from growbuddies.influxdb_code import ReadingsStore
import sys






class Callbacks:
    """The Callbacks class contains two callback functions that are passed to `MQTTServer`. These functions are activated when MQTTService receives
    an `on_message` event for the corresponding topics associated with the callbacks.

    hello .. and then :py:class:`growbuddies.mqtt_code.MQTTService.start`

    :py:meth:`growbuddies.Callbacks.on_snifferbuddy_readings`


    """

    def __init__(self):

        self.logger = LoggingHandler()
        self.mistbuddy = MistBuddy()
        settings = Settings()
        settings.load()
        self.table_name = settings.get("snifferbuddy_table_name")
        self.readings_store = ReadingsStore()

    def on_snifferbuddy_readings(self, msg):
        """documenting the on_snifferbuddy_readings callback"""
        # Translate the mqtt message into a SnifferBuddy class.
        s = SnifferBuddyReadings(msg)
        self.logger.debug(f"the snifferbuddy values: {s.dict}")
        on_or_off_str = "ON" if self.mistbuddy.isLightOn(s.light_level) else "OFF"
        self.logger.debug(f"The light is {on_or_off_str}")
        # Adjust vpd. vpd is most relevant when the plants are transpiring when the lights are on.
        if self.mistbuddy.isLightOn(s.light_level):
            self.mistbuddy.adjust_humidity(s)
        # Store readings
        if self.table_name:
            self.readings_store.store_readings(s.dict)

    # The vpd value is returned. Turn on and off the humidifier based on it's value.

    def on_snifferbuddy_status(self, status):
        """

        .. note::

           How SnifferBuddy's status is determined is discussed in :ref:`mqtt_LWT`.


        "This callback function handles MQTT Last Will and Testament (LWT) messages regarding the online status of SnifferBuddy,
        which can be either "online" or "offline."

        Args:
            status (str): Either the string "Online" or "Offline".
        """
        self.logger.debug(f"-> SnifferBuddy is: {status}")
        # TODO: send alert if offline since snifferbuddy readings are the heartbeat.


def main():
    """The steps to adjust to an ideal vpd value include:

    1. Receive SnifferBuddy MQTT messages.  One message contains air readings such as CO2, humidity, temperature.  The other message contains
    status information on the SnifferBuddy device. the msg.payloag for the status mqtt message is either "online" or "offline".

    2. The vpd value is calculated from the temperature and humidity.  This is handled by the `SnifferBuddyReadings()` class.

    The Settings class reads in parameters used by the GrowBuddies from
    the `growbuddy_settings.json <https://github.com/solarslurpi/GrowBuddies/blob/main/growbuddiesproject/growbuddies/growbuddies_settings.json>`_
    file. One of these parameters is a dictionary containing information for subscribing to SnifferBuddy's MQTT topics. The MQTTService class uses
    this dictionary to determine which callback function to use when it receives a message. Specifically, it will use the readings callback if the
    message contains air readings, or the status callback if the message contains SnifferBuddy status information such as "online" or "offline".

    .. code-block:: json

        "snifferbuddy_mqtt_dict":
                                    {"tele/snifferbuddy/SENSOR": "on_snifferbuddy_readings",
                                     "tele/snifferbuddy/LWT": "on_snifferbuddy_status"},


    The above is the default entry.  The topic is the dictionary's key.  The name of the callback function is the value.  Notice this script includes
    the two methods :meth:`Callbacks.on_snifferbuddy_readings` and :meth:`Callbacks.on_snifferbuddy_status`.

    """
    # Keep collecting capacitive touch readings from DripBuddy
    settings = Settings()
    settings.load()
    obj = Callbacks()
    methods = settings.get_callbacks("snifferbuddy_mqtt_dict", obj)
    mqtt_service = MQTTService(methods)
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
