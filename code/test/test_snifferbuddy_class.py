
# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growbuddy/code')

import json
import pytest

from snifferbuddy_code import snifferBuddy


@pytest.fixture(scope="module")
def sb():
    # Testing with snifferbuddy formed mqtt message.
    sb = None
    try:
        with open("scd30_mqtt.json") as json_file:
            dict = json.load(json_file)
            print(f"{dict}")
            sb = snifferBuddy(dict)
    except FileNotFoundError as e:
        print(f"ERROR - message: {e}")
    return sb


def test_temperature() -> None:
    s = None
    with open("code/test/scd30_mqtt.json") as json_file:
        dict = json.load(json_file)
        print(f"{dict}")
        s = snifferBuddy(dict)
    print(f"{s.temperature}")
    assert (s.temperature > 0.0)

if __name__ == "__main__":
    test_temperature()
