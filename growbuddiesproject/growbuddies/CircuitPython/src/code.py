
# Version 0.15

import analogio
import board
import json
import math
import socketpool
import time
import wifi
import adafruit_scd4x
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from microcontroller import watchdog as w
from watchdog import WatchDogMode

DEBUG=True  # Set to False to turn of debug print statements.

# I guess using globals are bad..but hmmm....
light_on_pin = analogio.AnalogIn(board.A0)
i2c = board.STEMMA_I2C()
scd4x = adafruit_scd4x.SCD4X(i2c)

try:
    from config import config
except ImportError:
    debug_print("There is config info missing.  We need the config.py config file!")
    raise
#####################################################################
def debug_print(*args):
    if DEBUG:
        print(*args)
#####################################################################
def connect_wifi(ssid: str, password: str) -> None:
    try:
        debug_print(f"CONNECTING TO: {ssid}")
        wifi.radio.connect(ssid, password)
        debug_print(f"SUCCESSFULLY CONNECTED. {wifi.radio.ipv4_address}")

    except ConnectionError as e:
        debug_print(f"Error: {e} ")
        sys.exit(1)  # TODO: This doesn't seem to be the best way to exit...
#####################################################################
def connect_mqtt() -> MQTT.MQTT:
    pool = socketpool.SocketPool(wifi.radio)
    broker = config.get("mqtt_broker", "gus")
    port = config.get("mqtt_port",1883)
    debug_print(f"BROKER: {broker}  PORT: {port}")

    mqtt_client = MQTT.MQTT(
        broker= "gus",
        port=1883,
        keep_alive=120,
        socket_pool=pool,
    )
    # The LWT message is only sent if the client disconnects abnormally.
    # Process: 1) Publisher sets last will message 2) Broker detects connection break 3) Broker sends last will message to topic subscribers.
    # The broker waits for one and a half keepAlive periods before disconnecting the client and then sending the LastWillMessage.
    device_name = config.get("name","")
    if not device_name:
        debug_print(f"UHOH! In connect_mqtt() -> No device name")
    topic =f"snifferbuddy/{device_name}/lwt"
    # Must be called before connect().
    # Once we let the broker take over letting devices who have subscribed to this topic, they will know after 120+60 = 180 (one one-half keep-alive)
    # seconds after this device rudely disconnects.
    mqtt_client.will_set(topic=topic,payload="offline", qos=1,retain=False)
    mqtt_client.on_connect = connected
    mqtt_client.on_message = process_calibrate_message

    try:
        # I am having trouble resolving with DNS name...so use ip addr...hmmm...
        mqtt_client.connect(host=config["host_ip"])

    except Exception as e:
        debug_print("Error connecting to MQTT broker:", e)
        raise e

    return mqtt_client

#####################################################################
def connected(
    client: MQTT.MQTT, userdata: Dict[str, Any], flags: Dict[str, Any], rc: int
) -> None:

    debug_print("\nConnected to MQTT broker!\n")
    debug_print(f"Flags: {flags}\nRC: {rc}\nUser Data: {userdata}")
    device_name = config.get("name","")
    if not device_name:
        debug_print(f"In connected() -> UGH NO DEVICE NAME!")
    topic = "snifferbuddy/calibrate/" +device_name+"/#"
    client.subscribe(topic)
    debug_print(f"subscribed to {topic}")
#####################################################################
def process_calibrate_message( client, topic, message) -> None:
    '''
    Calibration in the context of the SCD4x is for either the CO2 or temperature.
    For CO2, there is an API for setting the CO2 based on an external CO2 reading.
    For temperature, there is the on-chip signal compensation API.  The calibration
    methods are discussed in the document.
    Since the grow tent's light being on and off is dependent on a photoresistor, the
    other parameter that can be calibrated is the light_threshold.
    '''

    adjustment_list = ['temperature', 'co2', 'light_threshold']

    debug_print("RECEIVED CALIBRATION MESSAGE")
    debug_print(f"topic: {topic}")
    debug_print(f"Message: {message}")
    _, _, device_name, param_type = topic.rstrip().split('/')
    debug_print(f"Device name {device_name} param_type: **{param_type}**")
    if param_type not in adjustment_list:
        debug_print(f" {param_type} is not in {adjustment_list}")
        return
    calibrate(param_type,float(message))
#####################################################################
def calibrate(param_type, calibration_value):
    debug_print(f"\n---> CALIBRATE. Param Type: {param_type} Calibration Value: {calibration_value}")
    # Use the CircuitPython's SCD4X API for Forced recalibration (FRC)
    min_co2_value = 400
    max_co2_value = 1500
    # CO2 CALIBRATION
    if param_type.lower() == 'co2':
        if min_co2_value < calibration_value < max_co2_value:
            scd4x.force_calibration(calibration_value)
        else:
            debug_print(f"\nIn calibrate() - UGH won't calibrate. The co2 reading: {calibration_value} is over {max_co2_value} or under {min_co2_value}.  Please help!")
    # TEMPERATURE CALIBRATION
    elif param_type.lower() == 'temperature':
        debug_print(f"\n param type is temperature!. calibration value unit is {config.get("temperature_unit","F")}")
        # The callibration_value is the temperature reading of the external source.
        # Temp(offset_actual) = Temp(SCD4x in celsius) - Temp(calibration_value in celsius)
        # By default, the temperature offset is 4. See section 3.6 in the datasheet. I think what is going on is
        # The default offset of 4 represents their take on the absolute maximum of additional heat from the electronics
        # close enough to the sensor to add heat to the reading.  So temperature_offset is perhaps thought to be at most 4.

        # Get a sensor reading.
        while not scd4x.data_ready:
            pass
        temp_unit = config.get("temperature_unit","F")
        # Calibration is done in C, so convert to C if the temperature unit is F.
        snifferbuddy_temperature = scd4x.temperature
        calibration_value = (calibration_value - 32)* 5/9 if temp_unit == "F" else calibration_value
        debug_print(f"SnifferBuddy's current temperature is: {snifferbuddy_temperature} ")
        debug_print(f"Calibration value: {calibration_value}")
        temp_offset = snifferbuddy_temperature - calibration_value
        if temp_offset < 0.0: # Numbers get wonky if there is a negative offset.  Calibration value must be < sensor reading.
            debug_print(f"temp offset is: {temp_offset} -> negative. Can't be negative")
            return

        # Must turn off the sensor taking readings and turn it into the mode to accept commands
        scd4x.stop_periodic_measurement()
        # Wait a bit (at least 1 second)
        time.sleep(2)
        debug_print(f"--->scd4x's current temperature_Offset is: {scd4x.temperature_offset}")

        debug_print(f"new temperature offset: {temp_offset}")
        time.sleep(2)

        #scd4x.temperature_offset = 4 # Default to accomodate heat.
        scd4x.temperature_offset = temp_offset
        scd4x.start_periodic_measurement()
        # If not called, the offset will not persist through reboots.
        scd4x.persist_settings()
    # TODO: LIGHT_THRESHOLD --> challenge...might require writing to Flash (config.py).  The challenge there is doing a pull down on QT PY because there is no switch.

#####################################################################
def read_and_publish_scd4x_data(mqtt_client):
    # Sadly, the sensor seems to freeze up at random times around 24 hours....
    w.timeout = 40  # After 40 seconds without finishing the loop will cause a reboot.
    w.mode = WatchDogMode.RAISE # Reboot.
    scd4x.start_periodic_measurement()
    debug_print("Waiting for first measurement....")
    reading_count = 0
    # From observation, it appears the first reading is without offset applied thus higher than it should be.
    # In fact, it appears to take some time for the readings to  adjust to the temp offset (default = 4 degrees C)
    skip_readings = 12

    while True:
        mqtt_client.loop()
        try:
            if scd4x.data_ready:
                reading_count += 1
                debug_print(f"reading count: {reading_count}")
                if reading_count > skip_readings:
                    reading_dict = build_reading_dict()
                    publish_reading_dict(reading_dict, mqtt_client)
            else:
                debug_print("No scd4x data ready")
        except BaseException:
            microcontroller.reset()
        time.sleep(1)  # Rest for a bit
        w.feed()  # Haven't frozen yet!s
        w.feed()  # Haven't frozen yet!
#####################################################################
def build_reading_dict():
    vpd = calc_vpd(scd4x.temperature, scd4x.relative_humidity)
    light_threshold = config.get('light_threshold',45000)
    light_state = 1 if light_on_pin.value > light_threshold else 0
    debug_print(f"light_on_pin.value: {light_on_pin.value} light_threshold: {light_threshold}")
    temp_unit = config.get("temperature_unit","F")
    debug_print(f"temp_unit: {temp_unit}")
    if temp_unit and temp_unit == "F":
        #convert to Fahrenheit
        temperature = scd4x.temperature* 9 / 5 + 32
    else:
        temperature = scd4x.temperature
    sensor_reading = {
    "name": config.get("name", "??"),
    "version": config.get("version", "??"),
    "light": light_state,
    "vpd": vpd,
    "co2": scd4x.CO2,
    "humidity": scd4x.relative_humidity,
    "temperature": temperature,
    "unit": config.get("temperature_unit", ""),
    }
    return sensor_reading

#####################################################################
def saturation_vapor_pressure(temp_celsius: float) -> float:
    """
    Calculates the saturation vapor pressure for a given temperature.

    Parameters:
    temp_celsius (float): Temperature in Celsius.

    Returns:
    float: The saturation vapor pressure in kPa.
    """
    return 0.6108 * math.exp((17.27 * temp_celsius) / (temp_celsius + 237.3))

#####################################################################
def calc_vpd(air_T_celsius: float, RH: float) -> float:
    leaf_T_celsius = air_T_celsius - 2

    saturation_vapor_pressure_air = saturation_vapor_pressure(air_T_celsius)
    saturation_vapor_pressure_leaf = saturation_vapor_pressure(leaf_T_celsius)

    actual_vapor_pressure_air = RH * saturation_vapor_pressure_air / 100

    vpd = saturation_vapor_pressure_leaf - actual_vapor_pressure_air

    return round(vpd, 2)
#####################################################################
def publish_reading_dict(reading:Dict, mqtt_client) -> None:

    sensor_type = config.get("sensor_type","")
    if sensor_type:
        reading = {sensor_type: reading}
        payload_topic = config.get("payload_topic","")
        debug_print(f" Payload topic: {payload_topic}")
        if payload_topic:
            payload = json.dumps(reading)
            try:
                mqtt_client.publish(payload_topic, payload)
                debug_print("Published:", payload)
            except:
                debug_printf(f"MQTT Publish failed.  Please check if the broker is known and available.")

        else:
            debug_print(f"Could not publish to the topic: {payload_topic}")
    else:
        debug_print(f"Invalid sensor type")


def main() -> None:
    ssid = config.get("wifi_ssid","")
    pwd = config.get("wifi_password","")
    if not ssid or not pwd:
        debug_print(f" Either the ssid: {ssid} or the password: {pwd} is missing.  Please check config.py")
        return
    debug_print("scd4x serial number:", [hex(i) for i in scd4x.serial_number])
    connect_wifi(ssid,pwd)
    debug_print("Waiting to connect to mqtt broker")
    mqtt_client = connect_mqtt()
    scd4x_reading = read_and_publish_scd4x_data(mqtt_client)
#####################################################################
if __name__ == "__main__":
    main()
