#
# manage_co2 adjusts the co2 within a grow tent based on a co2 setpoint.
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

from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings
from growbuddies.mqtt_code import MQTTService
from growbuddies.snifferbuddyreadings_code import SnifferBuddyReadings
from growbuddies.stomabuddy_code import StomaBuddy
import sys


class Callbacks:
    def __init__(self):
        self.logger = LoggingHandler()
        self.stomabuddy = StomaBuddy()

    def on_snifferbuddy_readings(self, msg):
        # Translate the mqtt message into a SnifferBuddy class.
        s = SnifferBuddyReadings(msg)
        if s.valid_packet:
            self.logger.debug(f"the snifferbuddy values: {s.dict}")
            on_or_off_str = s.light_level.upper()
            self.logger.debug(f"The light is {on_or_off_str}")
            # Adjust co2 when plants are transpiring.  Transpiration happens when the lights
            # are on.
            if on_or_off_str == "ON":
                self.stomabuddy.adjust_co2(s.co2)

    # The vpd value is returned. Turn on and off the humidifier based on it's value.

    def on_snifferbuddy_status(self, status):
        self.logger.debug(f"-> SnifferBuddy is: {status}")
        # TODO: send alert if offline since snifferbuddy readings are the heartbeat.


def main():
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
