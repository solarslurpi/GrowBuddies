
(snifferbuddy_doc)=
# SnifferBuddy
This guide details the process of assembling SnifferBuddy, configuring its software, and understanding its operation.
```{figure} images/SnifferBuddy_mqtt.png
:align: center
:height: 350

A SnifferBuddy with an SCD-40 Sensor Sending Readings over MQTT
```

SnifferBuddy broadcasts MQTT messages packed with SCD-4x sensor data. Node-red, home assistant, and any software tuned to SnifferBuddy's MQTT topic can pick up and utilize this data. Additionally, another GrowBuddies device - Gus, a Raspberry Pi server, can archive SnifferBuddy data in an influx db while optionally controlling VPD and CO2 levels.
Here is an example payload:
```
{"scd41": {"vpd": 1.43, "temperature": 78.314, "name": "sunshine", "light": "OFF", "co2": 929, "humidity": 45.5017, "unit": "F", "version": 0.1}}
```

## Build Steps
### 1. Get the parts together

The hardware needed to build SnifferBuddy includes:

| Component | Cost | Reason |
|-----------|------|--------|
| [QT Py ESP32-S2](https://www.adafruit.com/product/5325) | $12.50 | Excellent quality.  Easy to use with CircuitPython and WiFi. STEMMA connector makes it easy to connect the SCD-40 or 41.  Small size.
| [USB-C DATA Cable](https://amzn.to/3OW5SdE) | $10 | Includes wires for data transfer.  There are probably more inexpensive cables.  Please make sure to use one with data wires.
| [SCD-40 BoB](https://www.adafruit.com/product/5187) | $44.95 | Excellent quality.  Provides accurate CO2 readings.  STEMMA connector makes it easy to connect to the QT PY.
| [JST SH 4-Pin Cable](https://www.adafruit.com/product/4399) | $0.95 | Excellent quality. Connects the QT PY to the SCD-4x. No soldering required.
| Photoresistor | pennies | At some point I bought [a pack of photoresistors on Amazon](https://www.amazon.com/s?k=photoresistor).
| 10K  Resistor | pennies | As with photoresistors, I bought [a pack of resistors on Amazon](https://www.amazon.com/s?k=resistor).
| wiring | pennies | I like to use [silicone wires like this wire kit on Amazon](https://amzn.to/3C6chLU).
| enclosure | pennies | The files are found TBD.....



:::{dropdown} SnifferBuddy Hardware Meanderings (Other hardware options)
I've tried different hardware with previous SnifferBuddy builds.
:::


### 2. Print out the Enclosure
```{figure} images/snifferbuddy_on_printbed.jpg
:align: center
:height: 350

Top and Bottom Rings of the SnifferBuddy enclosure.
```
#### a. Download the Files

Print out these files on your 3D printer:
- Top Ring: Print out [scd40-ring.3mf](../enclosures/SnifferBuddy/scd-40/scd40-ring.3mf).
- Bottom Ring: Print out [bottom_qtpy.3mf](../enclosures/SnifferBuddy/scd-40/bottom_qtpy.3mf).

(_connect_wires)=
### 3. Connect Wires
- Connect the photoresistor wiring.  This requires a bit of soldering.
```{figure} images/SnifferBuddy_photoresistor_wiring.png
:align: center
:height: 350

Diagram of Photoresistor Wiring
```
```{figure} images/snifferbuddy_photoresistor_wiring_real.jpg
:align: center
:height: 350

QT Py wired with the Photoresistor circuit.
```
- Connect the QT Py and the SCD40.
```{figure} images/snifferbuddy_connected_scd4x.jpeg
:align: center
:height: 350

QT Py connected to scd4x sensor using Adafruit's STEMMA QT
```
### 4. Install CircuitPython onto the QT Py

Follow [Adafruit's instructions](https://learn.adafruit.com/adafruit-qt-py-esp32-s2/circuitpython).

```{note}
The CircuitPython version tested for compatibility with SnifferBuddy was 8.1.0.
```

### 5. Download Files To CircuitPython's Root Dir
{material-regular}`celebration;1em;sd-text-blue`  It is so wonderfully amazing that we can just drag and drop files onto our QT Py {material-regular}`celebration;1em;sd-text-blue`

Download these two files to the CIRCUITPY drive:

{material-regular}`download;1em;sd-text-success` [code.py](../growbuddiesproject/growbuddies/CircuitPython/src/code.py)
   - contains all of SnifferBuddy's code.  The code is discussed [later](_code_doc).

{material-regular}`download;1em;sd-text-success` [conf.json](../growbuddiesproject/growbuddies/CircuitPython/src/config.json)
   - contains all the values that can be changed.  The contents of the config file is discussed below.
### 6. Edit then Save the config file
The contents of the config file are listed below.  At a minimum, the wifi ssid and password must be set.

```{eval-rst}
.. literalinclude:: ../growbuddiesproject/growbuddies/CircuitPython/src/config.json

```
- **name and version**: The 'name' field distinguishes each SnifferBuddy when multiple units are used. The 'version' field indicates the code version running on each SnifferBuddy's QT Py microcontroller, ensuring accurate tracking of software updates.
- **wifi ssid and password**:  **Before deploying SnifferBuddy, it's essential to update these values** to align with your home network's WiFi settings.
- **mqtt broker and port**: Use any MQTT broker.  By default, the MQTT broker is Gus.  The default MQTT port is 1883.
- **temperature_unit**: The value is either an "F" or a "C", depending if readings should be stored in Fahrenheit or in Celsius.
- **sensor_type**: Supported types include scd40 and scd41.
- **light_threshold**: It is essential to know whether the grow light is on or off. SnifferBuddy uses the Photoresistor as a means to determine the relative light level.  As shown in the diagram within the [wiring section](_connect_wires), the light level is read from an analog pin on the QT Py.  The Photoresistor is the bottom resistor in the Voltage Divider circuit.  This means the more light, the higher the reading will be for the light level.  When code.py is run from Mu, print statements will show the light reading as shown below:

```
Published: {"scd41": {"vpd": 1.43, "temperature": 78.314, "name": "sunshine", "light": "OFF", "co2": 929, "humidity": 45.5017, "unit": "F", "version": 0.1}}
light reading: 45735
```
In this case, the reading is 45,735.  You may want to experiment to find the "ideal" threshold value for your setup.  It turned out 51000 was the ideal value for mine.
- **log_topic**: The MQTT topic used by the logging handler to send log messages to the MQTT broker.
- **lwt_topic**: Used along with **offline_payload** to set the Last Will and Testament. The **online_payload** is sent to the **lwt_topic** upon receiving a callback from the MQTT Broker that SnifferBuddy has connected.
```
    mqtt_client.will_set(config["lwt_topic"], config["offline_payload"], retain=True)
```
- **payload_topic**: The topic used to send the light info and scd4x readings.
### 7. Download Library Files to the lib Directory
Create the lib directory on your CIRCUITPY drive.

#### a. Download to the CIRCUITPY/lib directory:
{material-regular}`download;1em;sd-text-success` [log_mqtt.py](../growbuddiesproject/growbuddies/CircuitPython/src/log_mqtt.py)
#### b. Download the CircuitPython Libraries
Based on the version of CircuitPython you installed on the QT Py, download the [corresponding CircuitPython Libraries](https://circuitpython.org/libraries).
#### c. Copy Libraries to the CIRCUITPY/lib directory:
The following libraries need to be copied to CIRCUITPY/lib:
- adafruit_minimqtt
- adafruit_logging.mpy
- adafruit_scd4x.mpy

(_code_doc)=
## Code Documentation
Starting at the `main()` function:
```{eval-rst}
.. automodule:: growbuddies.CircuitPython.src.code
   :members: main

```


```{eval-rst}
.. autofunction:: growbuddies.CircuitPython.src.code.load_config
.. autofunction:: growbuddies.CircuitPython.src.code.connect_wifi
.. autofunction:: growbuddies.CircuitPython.src.code.connect_mqtt
.. autofunction:: growbuddies.CircuitPython.src.code.read_and_mqtt_scd4x_data
.. autofunction:: growbuddies.CircuitPython.src.code.process_light_info
```