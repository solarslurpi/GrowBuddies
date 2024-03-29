#
# version 0.12
#
try:
    from typing import Dict, Any
except:  # The typing library is not supported on CP.  It is here to support Sphinx documentation.
    pass
import sys
import time

import json
import board
import analogio
import adafruit_scd4x

# See https://learn.adafruit.com/circuitpython-essentials/circuitpython-resetting
import microcontroller
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import math
from microcontroller import watchdog as w
from watchdog import WatchDogMode

try:
    from config import config
except ImportError:
    print("There is config info missing.  We need the config.py config file!")
    raise


# FUNCTION DEFINITIONS
def connected(
    client: MQTT.MQTT, userdata: Dict[str, Any], flags: Dict[str, Any], rc: int
) -> None:
    """
    Executes when the MQTT client successfully connects to the MQTT broker.

    Parameters:
    client (MQTT.MQTT): The MQTT client.
    userdata (dict): Contains the Last Will Topic and the payload for "online" status.
    flags (dict): Broker's response flags.
    rc (int): Connection result.
    """
    # print("\nConnected to MQTT broker!\n")
    # print(f"Flags: {flags}\nRC: {rc}\nUser Data: {userdata}")
    # Publish that we are up and running!
    client.publish(userdata["lwt_topic"], userdata["online_payload"], retain=True)


def disconnected(client: MQTT.MQTT, userdata: Dict[str, Any], rc: int) -> None:
    print("DISCONNECTED FROM MQTT BROKER....")


def validate_config() -> bool:
    """
    Validates the configuration data by checking for all expected keys.
    """
    expected_keys = [
        "name",
        "version",
        "wifi_ssid",
        "wifi_password",
        "host_ip",
        "mqtt_broker",
        "mqtt_port",
        "temperature_unit",
        "sensor_type",
        "light_threshold",
        "log_topic",
        "lwt_topic",
        "payload_topic",
        "offline_payload",
        "online_payload",
    ]

    missing_keys = [key for key in expected_keys if key not in config]

    if missing_keys:
        return False
    return True


def get_temperature_unit(temp_c: float, unit: str) -> float:
    """
    Converts temperature from Celsius to Fahrenheit if necessary.

    Parameters:
    temp_c (float): Temperature in Celsius.
    unit (str): Desired temperature unit ("C" or "F").

    Returns:
    float: Temperature in the desired unit.
    """
    if unit == "F":
        return temp_c * 9 / 5 + 32
    return temp_c


def saturation_vapor_pressure(temp_celsius: float) -> float:
    """
    Calculates the saturation vapor pressure for a given temperature.

    Parameters:
    temp_celsius (float): Temperature in Celsius.

    Returns:
    float: The saturation vapor pressure in kPa.
    """
    return 0.6108 * math.exp((17.27 * temp_celsius) / (temp_celsius + 237.3))


def calc_vpd(air_T_celsius: float, RH: float) -> float:
    """
    Calculates the Vapor Pressure Deficit (VPD).

    Parameters:
    air_T_celsius (float): Air temperature in Celsius.
    RH (float): Relative Humidity.

    Returns:
    float: The VPD in kPa.
    """
    leaf_T_celsius = air_T_celsius - 2

    saturation_vapor_pressure_air = saturation_vapor_pressure(air_T_celsius)
    saturation_vapor_pressure_leaf = saturation_vapor_pressure(leaf_T_celsius)

    actual_vapor_pressure_air = RH * saturation_vapor_pressure_air / 100

    vpd = saturation_vapor_pressure_leaf - actual_vapor_pressure_air

    return round(vpd, 2)


def connect_wifi(ssid: str, password: str) -> None:
    """
    Connects to a Wi-Fi network based on the ssid and password that are
    passed in.

    Parameters:
    ssid (str): SSID of the Wi-Fi network.
    password (str): Password for the Wi-Fi network.


    Raises:
    SystemExit: If connection to the Wi-Fi network fails.
    """
    # CONNECT TO WIFI
    try:
        print(f"CONNECTING TO: {ssid}")
        wifi.radio.connect(ssid, password)
        print(f"SUCCESSFULLY CONNECTED. {wifi.radio.ipv4_address}")

    except ConnectionError as e:
        print(f"Error: {e} ")
        sys.exit(1)


def subscribed(
    client: MQTT.MQTT, userdata: Dict[str, Any], flags: Dict[str, Any], rc: int
) -> None:
    print("IN SUBSCRIBED FOR LWT MESSAGES")


def connect_mqtt() -> MQTT.MQTT:
    """
    Establishes connection to an MQTT broker. By default, the broker
    is Gus.  Gus is a Raspberry Pi GrowBuddy that runs the Mosquitto mqtt broker service
    as well as influxdb for storing readings, Grafana for charting, and services for
    maintaining a vpd setpoint and CO2 level.  However, any mqtt broker will work.

    Returns:
    MQTT.MQTT: The MQTT client.

    Raises:
    SystemExit: If connection to the MQTT broker fails.
    """
    ## Create a socket pool for handling network connections
    pool = socketpool.SocketPool(wifi.radio)
    lwt_data = {
        "lwt_topic": config["lwt_topic"],
        "online_payload": config["online_payload"],
    }
    mqtt_client = MQTT.MQTT(
        broker=config["mqtt_broker"],
        port=config["mqtt_port"],
        keep_alive=300,
        user_data=lwt_data,
        socket_pool=pool,
    )
    mqtt_client.will_set(config["lwt_topic"], config["offline_payload"], retain=True)
    mqtt_client.on_connect = connected
    mqtt_client.on_disconnect = disconnected
    mqtt_client.on_subscribe = subscribed

    try:
        # I am having trouble resolving with DNS name...so use ip addr...hmmm...
        mqtt_client.connect(host=config["host_ip"])

    except Exception as e:
        print("Error connecting to MQTT broker:", e)
        raise e

    return mqtt_client


def process_light_info(light_reading: int, threshold: int) -> str:
    """
    Processes light information based on threshold settings.

    Parameters:
    light_reading (int): Photoresistor reading from QT Py's analog pin.
    threshold (int): The threshold value determines if the grow light is on or off.  The photoresistor is at the bottom of the voltage divider circuit.  Thus, the light level goes higher when the light intensity increases.

    Returns:
    str: State of the light ("ON" or "OFF").
    """
    light_state = "OFF"

    if light_reading > threshold:
        light_state = "ON"
    return light_state


def build_sensor_data(light_state: str, scd4x: adafruit_scd4x.SCD4X) -> Dict[str, Any]:
    """
    Builds sensor data for MQTT payload.

    Parameters:
    config (dict): Configuration data.
    light_state (str): State of the light ("ON" or "OFF").
    scd4x (adafruit_scd4x.SCD4X): SCD4X sensor object.

    Returns:
    dict: Sensor data.
    """
    vpd = calc_vpd(scd4x.temperature, scd4x.relative_humidity)
    temperature_rounded = round(scd4x.temperature, 2)
    sensor_data = {
        "name": config["name"],
        "version": config["version"],
        "light": light_state,
        "vpd": vpd,
        "co2": scd4x.CO2,
        "humidity": scd4x.relative_humidity,
        "temperature": get_temperature_unit(
            temperature_rounded, config["temperature_unit"]
        ),
        "unit": config["temperature_unit"],
    }
    return sensor_data


def publish_sensor_data(
    mqtt_client: MQTT.MQTT,
    sensor_type: str,
    sensor_data: Dict[str, Any],
    payload_topic: str,
) -> None:
    """
    Publishes sensor data to a specified MQTT topic.

    Parameters:

    mqtt_client (MQTT.MQTT): The MQTT client.
    sensor_type (str): Type of the sensor.
    sensor_data (dict): Sensor data.
    payload_topic (str): MQTT topic to publish the sensor data.
    """
    reading = {sensor_type: sensor_data}
    payload = json.dumps(reading)
    mqtt_client.publish(payload_topic, payload)
    # print("Published:", payload)


def read_and_mqtt_scd4x_data(
    analog_in: analogio.AnalogIn, mqtt_client: MQTT.MQTT
) -> None:
    """
    Continuously reads data from the SCD4X sensor and publishes it via MQTT. This function
    also utilizes a watchdog timer to ensure the reliability and robustness of the system.

    In the event of a software hang or a malfunction, the watchdog timer resets the system
    to recover normal operations. A log message notifying that the watchdog timer popped off
    is sent to the MQTT broker.  The timer is set to a specified timeout period, and during
    normal operation, the software must "kick" or reset the watchdog timer regularly before
    it reaches the timeout period. If the software fails to kick the watchdog in time, a
    system reset is triggered and a watchdog timeout message is sent to the mqtt broker.

    Parameters:

    config (dict): Configuration data including watchdog timeout.

    analog_in (analogio.AnalogIn): Analog input for light sensor.

    mqtt_client (MQTT.MQTT): The MQTT client.

    logger (adafruit_logging.Logger): Logger object, used to log system status and debug information.

    Raises:
    SystemExit: If reading data from the sensor or publishing it fails, or if the watchdog
    timer is not reset in time, indicating a possible system hang or malfunction.
    """
    mqtt_client.publish(config["log_topic"], "Start sending readings.")
    w.timeout = 40  # After 40 seconds without finishing the loop will cause a reboot.
    w.mode = WatchDogMode.RAISE
    i2c = board.STEMMA_I2C()
    scd4x = adafruit_scd4x.SCD4X(i2c)
    scd4x.start_periodic_measurement()
    count = 0
    w.mode = WatchDogMode.RAISE
    while True:
        try:
            if scd4x.data_ready:
                count += 1
                light_state = process_light_info(
                    analog_in.value, config["light_threshold"]
                )
                sensor_data = build_sensor_data(light_state, scd4x)
                publish_sensor_data(
                    mqtt_client,
                    config["sensor_type"],
                    sensor_data,
                    config["payload_topic"],
                )
                time.sleep(
                    4
                )  # Rest for a bit.  But less than the 5 sec default adafruit's minimqtt default keepalive of 5 secs.
                w.feed()  # Haven't frozen yet!
                time_passed = "{:.1f}".format(time.monotonic())
                mqtt_client.publish(
                    config["log_topic"],
                    f"{time_passed} | {count} readings have been published.",
                )
        except BaseException:
            microcontroller.reset()


def main() -> None:
    """
    Initiates the process of gathering scd4x readings and transmitting them via MQTT.

    Utilizing the parameters in the CONFIG_FILE (see :func:`load_config`), it:

    - sets up the analog pin to read in the photoresistor value.
    - establishes a connection to the Wi-Fi network (see :func:`connect_wifi`).
    - sets up an MQTT client and connects to the MQTT broker identified within the CONFIG_FILE (see :func:`connect_mqtt`).
    - sets up a logging handler to log code messages as MQTT messages (see :func:`set_mqtt_handler`).
    - hands it over to :func:`read_and_mqtt_scd4x_data` to continuously read the scd4x data and publish over MQTT.

    A logger is set to the MQTT client so that log messages can be published over MQTT.
    """
    if not validate_config():
        print("The config.py file is most likely missing entries.")
        # TODO on errors, blink LED or something?
        raise e
    analog_in = analogio.AnalogIn(board.A0)
    # Retrieve the ssid and password from the config file and then connect to the wifi.
    connect_wifi(config["wifi_ssid"], config["wifi_password"])
    try:
        mqtt_client = connect_mqtt()
    except RuntimeError as e:
        print(f"Error: {e}")
        raise e
    read_and_mqtt_scd4x_data(analog_in, mqtt_client)


if __name__ == "__main__":
    main()
