#
# manage_vpd adjusts the humidity within a grow tent based on a vpd setpoint.
#
# Copyright 2023 Happy Day

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
"""
manage_vpd.py
=============

This script utilizes MistBuddy to regulate the operation of the humidifier,
turning it on and off as necessary to maintain the optimal vapor pressure deficit (VPD) level.
The  :func:`main` function initiates the program by establishing
callback functions and subscribing to SnifferBuddy
readings through the :py:class:`growbuddies.mqtt_code.MQTTService` class. When a reading is received, the
:py:meth:`Callbacks.on_snifferbuddy_readings` callback activates the `MistBuddy()` class to turn on the humidifier if the vapor
pressure deficit (VPD) value exceeds the setpoint value in growbuddies_settings.json.


The growbuddy_settings.json file contains several parameters that are used as input for the program.

    .. code-block:: json

        "vpd_growth_stage": "veg",
        "vpd_setpoints": {
            "veg": 0.9,
            "flower": 1.0
            }


`vpd_growth_stage` lets MistBuddy know what growth stage the plants are in.  There are two stages:
- "veg" for vegetative.
- "flower" For the flowering stage.


The above settings are using by the MistBuddy code, see :py:meth:`Callbacks.on_snifferbuddy_readings`.  The settings indicate
the plants are currently in the vegetative growth stage. Based on the VPD chart, a good choice for the ideal VPD value for this
stage is 0.9. The VPD chart is a good reference for choosing the ideal VPD value for each growth stage.

    .. image:: ../docs/images/vpd_chart.jpg
        :scale: 50
        :alt: Flu's vpd chart
        :align: center

The two SnifferBuddy callbacks are sent to the MQTTService():

    .. code-block:: json

        "snifferbuddy_mqtt": {"tele/snifferbuddy/SENSOR": "on_snifferbuddy_readings",
                          "tele/snifferbuddy/LWT": "on_snifferbuddy_status"},

by passing in the "snifferbuddy_mqtt" keyword, the MQTTService() knows which callback goes with which MQTT topic, making it easy to
subscribe to the topic and then callback the callback functions when a message is received.

"""
from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings
from growbuddies.mqtt_code import MQTTService
from growbuddies.snifferbuddyreadings_code import SnifferBuddyReadings
from growbuddies.mistbuddy_code import MistBuddy
import sys


class Callbacks:
    """The Callbacks class contains two callback functions that are passed to `MQTTServer`. These functions
    are activated when MQTTService receives an `on_message` event for the corresponding topics associated with
    the callbacks.
    """

    def __init__(self):
        self.logger = LoggingHandler()
        self.mistbuddy = MistBuddy()

    def on_snifferbuddy_readings(self, msg):
        """This callback function handles MQTT messages from SnifferBuddy.  The payload is a JSON string that is converted
        into a :py:class:`growbuddies.snifferbuddyreadings_code.SnifferBuddyReadings` object. Methods in the :py:meth:`growbuddies.mistbuddy_code.MistBuddy` class is then
        called to adjust the humidity based on the vpd value.
        """
        # Translate the mqtt message into a SnifferBuddy class.
        s = SnifferBuddyReadings(msg)
        if s.valid_packet:
            self.logger.debug(f"the snifferbuddy values: {s.dict}")
            # The light level is a string either "ON" or "OFF".
            on_or_off_str = s.light_level.upper()
            self.logger.debug(f"The light is {on_or_off_str}")
            # Adjust vpd. vpd is most relevant when the plants are transpiring when the lights are on.
            if on_or_off_str == "ON":
                self.mistbuddy.adjust_humidity(s.vpd)

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
    status information on the SnifferBuddy device.

    2. The vpd value is calculated from the temperature and humidity.  This is handled by the :py:class:`growbuddies.snifferbuddy_readings.SnifferBuddyReadings` class.

    The Settings class reads in parameters used by the GrowBuddies from
    the `growbuddy_settings.json <https://github.com/solarslurpi/GrowBuddies/blob/main/growbuddiesproject/growbuddies/growbuddies_settings.json>`_
    file. One of these parameters is a dictionary containing information for subscribing to SnifferBuddy's MQTT topics. The MQTTService class uses
    this dictionary to determine which callback function to use when it receives a message. Specifically, it will use the readings callback if the
    message contains air readings, or the status callback if the message contains SnifferBuddy status information such as "online" or "offline".

    .. code-block:: json

        "snifferbuddy_mqtt":
                                    {"tele/snifferbuddy/SENSOR": "on_snifferbuddy_readings",
                                     "tele/snifferbuddy/LWT": "on_snifferbuddy_status"},


    The above is the default entry.  The topic is the dictionary's key.  The name of the callback function is the value.  Notice this script includes
    the two methods :meth:`Callbacks.on_snifferbuddy_readings` and :meth:`Callbacks.on_snifferbuddy_status`.

    """
    # Keep collecting capacitive touch readings from DripBuddy
    settings = Settings()
    settings.load()
    obj = Callbacks()
    methods = settings.get_callbacks("snifferbuddy_mqtt", obj)
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
