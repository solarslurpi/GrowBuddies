"""This Python script turns the mistBuddy's two power supplies on or off.
"""

# TODO: These two lines can be removed when this is part of a package.
import sys

sys.path.append("/home/pi/growbuddy/code")
from code.gus_code import growBuddy


def main():
    """We'll use growBuddy to send mqtt messages that turn the two Sonoff switches off."""

    on_or_off = None
    fan_or_mister = None
    mqtt_topic_key = None
    mqtt_topic_key = "mistBuddy_fan_topic"

    while (
        "FAN" != fan_or_mister and "MIST" != fan_or_mister and "BOTH" != fan_or_mister
    ):
        print("Enter FAN for fan power plug")
        print("Enter MIST for mister power plug")
        print("Enter BOTH to apply ON or OFF to both")
        fan_or_mister = input().upper()
    if "FAN" == fan_or_mister:
        mqtt_topic_key = "mistBuddy_fan_topic"
    else:
        mqtt_topic_key = "mistBuddy_mister_topic"

    while "ON" != on_or_off and "OFF" != on_or_off:
        print("Please enter ON or OFF")
        on_or_off = input().upper()
    if "BOTH" == fan_or_mister:
        mqttAccess1 = growBuddy(
            subscribe_to_sensor=False,
            topic_key="mistBuddy_fan_topic",
            msg_value=on_or_off,
        )
        mqttAccess1.start()

        mqttAccess2 = growBuddy(
            subscribe_to_sensor=False,
            topic_key="mistBuddy_fan_topic",
            msg_value=on_or_off,
        )
        mqttAccess2.start()
        # Turn plugs on
        # Publish the mqtt message to turn the plugs on.
    else:
        mqttAccess1 = growBuddy(
            subscribe_to_sensor=False, topic_key=mqtt_topic_key, msg_value=on_or_off
        )
        mqttAccess1.start()


if __name__ == "__main__":
    main()
