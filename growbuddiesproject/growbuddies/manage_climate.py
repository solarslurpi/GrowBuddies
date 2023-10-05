#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
# A challenge that should concern us is handling the unfortunate
# scenario in which the power switches have been turned on, but not off
# We:
# - Send two repeating messages to turn the power off when the
# amount of seconds it should be on runs out.
# - Use the mom service to send POWER OFF messages:
#    - when receive a mqtt message and when checking the vpd,
#    set a timer and send POWER OFF messages if the timer goes off.
#    - determine if the vpd is getting too low.  If it is, send POWER OFF messages.
# - Set a rule on the tasmotized power plugs:
# ```
# Rule1 ON Power1#State=1 DO PulseTime 200 ENDON
# Rule1 1
# ```
# The rule says when the power is turned on, wait 20 seconds and then turn it off.  The PulseTime is reset every time a new POWER ON message.
#/
# In manage_vpd.py
from growbuddies.snifferbuddy_handler import SnifferBuddyHandler
from growbuddies.climate_regulator import ClimateRegulator
from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings
import threading
print(f"MQTT handling is running in thread ID: {threading.get_ident()}")

def main():
    settings = Settings()
    settings.load()
    prime_rolling_window_size = settings.get('rolling_window_size',3)
    # mist_buddy = ClimateRegulator("MistBuddy_PID_key")
    stoma_buddy = ClimateRegulator("StomaBuddy_PID_key")
    mqtt_handler = SnifferBuddyHandler()
    logger = LoggingHandler()
    mqtt_handler.start()
    # Let's wait for a few readings before starting mist_buddy.
    message_count = 0
    start_adjustment = False
    ready_for_pid = False

    try:
        while True:
            # A message has for the type readings or status.
            # If readings, returns a SnifferBuddyReadings instance.
            message = mqtt_handler.get_message_from_queue()
            if message is not None:
                message_type, snifferbuddy_readings = message
                if message_type == "readings":
                    message_count += 1
                    # mist_buddy.add_value_to_window(snifferbuddy_readings["vpd"])
                    ready_for_pid = stoma_buddy.add_value_to_window(snifferbuddy_readings['name'], snifferbuddy_readings["co2"])
                    # mist_buddy.light_on = snifferbuddy_readings["light"]
                    stoma_buddy.light_on = snifferbuddy_readings["light"]
                    logger.debug(f"{message}")
                if ready_for_pid and not start_adjustment:
                    # mist_buddy.start()
                    stoma_buddy.start()
                    start_adjustment = True
    except KeyboardInterrupt:
        mqtt_handler.stop()
        stoma_buddy.stop()
        # mist_buddy.stop()


if __name__ == "__main__":
    main()
