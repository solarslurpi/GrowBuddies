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
from growbuddies.influxdb_code import ReadingsStore
import sys


class Callbacks:
    def __init__(self):
        self.logger = LoggingHandler()
        settings = Settings()
        settings.load()
        pid_settings = settings.get("StomaBuddy_PID_key")
        self.isTuning = True if pid_settings["tune"]["increment"] > 0 else False
        callback_method_dict = {}
        if self.isTuning:
            function_name = pid_settings["pid_callback"]
            pid_callback = getattr(self, function_name)
            callback_method_dict = {function_name: pid_callback}
            self.Kp = None
            self.table_to_store_readings = ReadingsStore(
                pid_settings["tune"]["influxdb_table_name"]
            )
        self.stomabuddy = StomaBuddy(callback_method_dict)
        # Used to keep track of the time since the light turned on.
        # This variable is needed by the adjust_co2() function.
        self.last_light_on_time = None

    def on_pid_callback(self, pid_values):
        self.Kp = pid_values["Kp"]
        print(pid_values)

    def on_snifferbuddy_readings(self, msg):
        # Translate the mqtt message into a SnifferBuddy class.
        self.logger.debug("Got message {msg} from snifferbuddy.")
        s = SnifferBuddyReadings(msg)
        if self.isTuning and self.Kp:
            s.dict.update({"Kp": round(self.Kp, 2)})
            self.table_to_store_readings.store_readings(s.dict)

        self.logger.debug(f"the snifferbuddy values: {s.dict}")
        on_or_off_str = s.light_level.upper()
        self.logger.debug(f"The light is {on_or_off_str}")
        # Adjust co2 when plants are transpiring.  Transpiration happens when the lights
        # are on.
        if on_or_off_str == "ON":
            # if self.last_light_on_time is None:
            #  self.last_light_on_time = time.time()
            # else:
            #     # Check if it has been 1/2 hour since the light turned on. This is a co2
            #     # conservation method based on "talk about" the stoma take time to fully
            #     # transition to full transpiration.
            #     if (time.time() - self.last_light_on_time) > 30 * 60:
            self.stomabuddy.adjust_co2(s.co2)
            self.last_light_on_time = None

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
