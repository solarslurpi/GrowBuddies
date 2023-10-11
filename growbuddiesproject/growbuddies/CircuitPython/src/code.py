
# Version 0.16

import analogio
import board
import json
import math
import socketpool
import supervisor
import time
import wifi
import adafruit_scd4x
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from microcontroller import watchdog as w
from watchdog import WatchDogMode

DEBUG=False  # Set to False to turn of debug print statements.

# I guess using globals are bad..but hmmm....TODO: Put into a class or two?
# CHECK WHICH PIN IS BEING USED!!!!
light_on_pin = analogio.AnalogIn(board.A3)
i2c = board.STEMMA_I2C()
scd4x = adafruit_scd4x.SCD4X(i2c)
#pool_udp = socketpool.SocketPool(wifi.radio)
#sock_udp = pool_udp.socket(pool_udp.AF_INET, pool_udp.SOCK_DGRAM) # UDP, and we'l reuse it each time

try:
    from config import config
except ImportError:
    debug_print("There is config info missing.  We need the config.py config file!")
    raise

host = config.get("host_name","gus.local")
port = config.get("udp_port",49152)
#####################################################################
def debug_print(*args):

    if DEBUG:
        print(*args)
    #else:
     #   message = ' '.join(map(str, args))  # Convert all arguments to strings and join them
     #   send_udp_message(message)  # Assuming send_udp_message expects a string

#####################################################################
# def send_udp_message(msg: str) -> None:
#     global sock_udp, host, port
#     debug_print(f"Sending to {host}:{port} message: {msg}")
#     bmsg = bytes(msg, 'utf-8')
#     try:
#         if sock_udp:
#             sock_udp.sendto(bmsg, (host,port) )  # send UDP packet to udp_host:port
#     except NameError as e:
#         print(f"NameError caught: {e}")
#    except socket.gaierror as e:
#        print(f"Error resolving hostname: {e}")


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
    global pool, host
    mqtt_broker = "192.168.68.113"
    # broker = config.get("mqtt_broker", "gus.local")
    port = config.get("mqtt_port",1883)
    #mqtt_port = 1883
    #debug_print(f"BROKER: {broker}  PORT: {port}")
    pool_mqtt = socketpool.SocketPool(wifi.radio)


    mqtt_client = MQTT.MQTT(
        broker= mqtt_broker,
        port=1883,
        keep_alive=120,
        socket_pool=pool_mqtt,
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
    # I have found subscribing can cause the system to freeze up.  I'd like to support
    # online calibration, but for now I will work on a more robust publishing of sensor readings.
    # mqtt_client.on_message = process_calibrate_message

    try:
        mqtt_client.connect(host=host)
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
    # I am commenting out but leaving in the code for calibration.  I was finding subscribing
    # created a system in which the mqtt client was more likely to freeze. I believe because the
    # mqtt_loop was needed...for now, focus on publishing the readings.
    #topic = "snifferbuddy/calibrate/" +device_name+"/#"
    #client.subscribe(topic)
    #debug_print(f"subscribed to {topic}")
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
    w.timeout = 20  # After x seconds without finishing the loop will cause a reboot.
    w.mode = WatchDogMode.RESET # Reboot
    scd4x.start_periodic_measurement()
    debug_print("Waiting for first measurement....")
    reading_count = 0
    # The datasheet recommended skipping at least the first two readings as the sensor adjusts.
    skip_readings = 3

    while True:
        # The loop() method checks incoming and process outgoing MQTT messages and works to
        # keep the connection between the broker and mqtt client alive.
        try:
            mqtt_client.loop()
        except Exception as e:
            debug_print(f"Error on call to mqtt_client.loop(). ERROR: {e}")
            supervisor.reload() # <CTRL-D>
        if scd4x.data_ready:
            reading_count += 1
            debug_print(f"reading count: {reading_count}")
            if reading_count > skip_readings:
                reading_dict = build_reading_dict()
                publish_reading_dict(reading_dict, mqtt_client)
        else:
            debug_print("No scd4x data ready")
        time.sleep(5)  # Takes a bit for each reading.
        w.feed()  # Let the watchdog timer know we are not frozen.
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
                mqtt_client.publish(payload_topic, payload, qos=0)
                debug_print("Published:", payload)
            except Exception as e:
                # I've noticed when the broker is flaky or rebooted, this can happen. So <CTRL><D>
                #supervisor.reload()
                debug_print(f"Could not publish to the topic: {payload_topic}. ERROR: {e}")
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
