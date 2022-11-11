
# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growBuddy/code')

import json
# import pytest

from snifferbuddy_code import snifferBuddy


def test_snifferbuddy_values() -> None:
    # The scd30_mqtt.json file contains an SnifferBuddy mqtt message from a snifferBuddy that
    # has an scd30 sensor.  This test opens the file as the mqtt dictionary and then checks the transfer
    # into snifferBuddy properties.
    s = None
    try:
        with open("code/test/scd30_mqtt.json") as json_file:
            mqtt_dict = json.load(json_file)
            print(f"{mqtt_dict}")
            # Translate between the mqtt_dict and the snifferBuddy values.
            s = snifferBuddy(mqtt_dict)
    except FileNotFoundError as e:
        print(f"ERROR - message: {e}")
    #  with capsys.disabled():
    print(f"Temperature: {s.temperature} | Humidity: {s.humidity} | CO2: {s.co2} | vpd {s.vpd} | light level {s.light_level}")
    # Check that the values are realistic.
    assert (0.0 < s.temperature)
    assert (0.0 < s.humidity <= 100.0)
    assert (0 < s.co2 <= 3000)
    assert (0.0 < s.vpd <= 3.0)
    assert (0 < s.light_level <= 1024)


test_snifferbuddy_values()
