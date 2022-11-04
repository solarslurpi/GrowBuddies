
# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growbuddy/code')

import json
# import pytest

from snifferbuddy_code import snifferBuddy


# def test_snifferbuddy_values(capsys) -> None:
def test_snifferbuddy_values() -> None:
    s = None
    try:
        with open("code/test/scd30_mqtt.json") as json_file:
            dict = json.load(json_file)
            print(f"{dict}")
            s = snifferBuddy(dict)
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
