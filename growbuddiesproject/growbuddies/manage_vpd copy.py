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
from growbuddies.snifferbuddy_handler import SnifferBuddyHandler
from growbuddies.logginghandler import LoggingHandler
from growbuddies.mistbuddy_code import MistBuddy
import time

logger = LoggingHandler()
mistbuddy = MistBuddy()


def manage_vpd(snifferbuddy_readings: dict) -> None:
    logger.debug(f"the snifferbuddy values: {snifferbuddy_readings}")
    # The light level is a string either "ON" or "OFF".
    on_or_off_str = snifferbuddy_readings["light"].upper()
    # logger.debug(f"The light is {on_or_off_str}")
    # Adjust vpd. vpd is most relevant when the plants are transpiring when the lights are on.
    if on_or_off_str == "ON":
        mistbuddy.adjust_humidity(snifferbuddy_readings["vpd"])


def main() -> None:
    """
    The main function initializes a SnifferBuddyHandler and listens for SnifferBuddy readings.
    It continuously checks the handler's message queue for new SnifferBuddy readings. If a new reading
    is available, it calls `manage_vpd` with the SnifferBuddyReading.  `manage_vpd` looks at the reading to check if the light in the grow area is on. If it is, the SnifferBuddy reading is sent to `mistbuddy` to turn on the humidifier if the vpd is higher than the setpoint.
    The function runs indefinitely until it is interrupted with a KeyboardInterrupt (Ctrl+C),
    at which point it stops the handler and exits.
    """
    handler = SnifferBuddyHandler()
    # Start listening for SnifferBuddy readings.
    handler.start()

    try:
        while True:
            message = handler.get_message_from_queue()
            if message is not None:
                message_type, snifferbuddy_readings = message
                if message_type == "readings":
                    manage_vpd(snifferbuddy_readings)

            time.sleep(0.5)
    except KeyboardInterrupt:
        handler.stop()


if __name__ == "__main__":
    main()
