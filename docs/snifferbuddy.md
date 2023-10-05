
(snifferbuddy_doc)=
# SnifferBuddy
## About
SnifferBuddy, a puck-shaped device, measures ambient conditions—temperature, humidity, CO2, and light status—in the grow tent using an SCD4x sensor and a photoresistor. It calculates VPD and publishes the data via MQTT.

```{figure} images/SnifferBuddy_mqtt.png
:align: center
:height: 350

A SnifferBuddy with an SCD-40 Sensor Sending Readings over MQTT
```
## Hardware
Opening up the SnifferBuddy,
```{figure} images/snifferbuddy_connected_scd4x.jpeg
:align: center
:height: 300

Inside a SnifferBuddy
```````
We see it is made of:
:::::{grid} 3

::::{grid-item-card} QTPY ESP32-S2
:img-top: images/qtpy_esp32-s2-icon.jpg
:img-alt:

[Link to Adafruit](https://www.adafruit.com/product/5325#technical-details)

::::

::::{grid-item-card} SCD4x
:img-top: images/adafruit_products_SDC41_top.jpg

[Adafruit SCD40](https://www.adafruit.com/product/5187)
+++
[Aliexpress SCD4x](https://www.aliexpress.us/item/3256804035401013.html)


::::
::::{grid-item-card} JST SH 4-Pin Cable
:img-top: https://cdn-shop.adafruit.com/970x728/4399-00.jpg

[Adafruit 50mm](https://www.adafruit.com/product/5187)

::::

:::::

:::::{grid} 3

::::{grid-item-card} Photoresistor
:img-top: https://m.media-amazon.com/images/I/51T9+GRwcvL._SX342_SY445_.jpg


[30 (~ $.20 each)](https://www.amazon.com/eBoot-Photoresistor-Sensitive-Resistor-Dependent/dp/B01N7V536K/ref=sr_1_3?keywords=photoresistor&sr=8-3)

::::

::::{grid-item-card} 12K Resistor
:img-top: https://m.media-amazon.com/images/I/51YOJThA2CL._SL1300_.jpg

[Pack of 100](https://www.amazon.com/EDGELEC-Resistor-Tolerance-Resistance-Optional/dp/B07HDGQRSR/ref=sr_1_1_sspa?keywords=12k%2Bresistor&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1)


::::
::::{grid-item-card} Silicon Cable
:img-top: https://m.media-amazon.com/images/I/61-4JvwAQ0L._AC_SY450_.jpg

[30 AWG Silicon Wire](https://amzn.to/3LHvDw0)

::::

:::::

This guide details the process of assembling SnifferBuddy, configuring its software, and understanding its operation.  See [Store Readings](store_readings.md) to see how SnifferBuddies' data can then be used.

SnifferBuddy broadcasts MQTT messages packed with SCD-4x sensor data. Node-red, home assistant, and any software tuned to SnifferBuddy's MQTT topic can pick up and utilize this data. Additionally, another GrowBuddies device - Gus, a Raspberry Pi server, can archive SnifferBuddy data in an influx db while optionally controlling VPD and CO2 levels.
Here is an example payload:
```
{"scd40": {"vpd": 1.43, "temperature": 78.314, "name": "sunshine", "light": "OFF", "co2": 929, "humidity": 45.5017, "unit": "F", "version": 0.1}}
```
## Glossary
- **MQTT (Message Queuing Telemetry Transport)**: A lightweight messaging protocol used for sending and receiving telemetry data in the form of messages between devices, servers, and applications. MQTT is especially useful in scenarios where network bandwidth is at a premium.
- **SCD-4x**: This refers to a series of CO2 sensors from Sensirion, specifically the SCD-40 and SCD-41 models. These sensors are integrated into breakout boards developed and sold by Adafruit. The breakout boards make it easier to interface with and use the sensors in projects. The Adafruit product pages for the [SCD-40](https://www.adafruit.com/product/5187) and [SCD-41](https://www.adafruit.com/product/5190) provide further details. SnifferBuddy uses this breakout board.
- **STEMMA Connector**: STEMMA is a standard adopted by Adafruit to make connecting sensors and devices easier, eliminating the need for soldering. It uses JST connectors, specifically JST PH for larger, power-focused connections and JST SH for smaller, data-focused connections. STEMMA connectors means connections don't require soldering or breadboarding {material-regular}`celebration;1em;sd-text-blue`.
- **QT Py ESP32-S2**: Adafruit's compact microcontroller, featuring an ESP32-S2 chip with built-in USB and Wi-Fi capabilities. It supports easy, solder-free connections to devices via a built-in STEMMA QT connector. More on [the product page](https://www.adafruit.com/product/5187).
- **CircuitPython**: An open-source derivative of MicroPython developed and maintained by Adafruit. The design intent is to simplify experimenting and learning to code on low-cost microcontroller boards. More on [the product page](https://circuitpython.org/)
(make_snifferbuddy)=
## Make SnifferBuddy
### 1. Get the parts together

The hardware needed to build SnifferBuddy includes:

| Component | Cost | Reason |
|-----------|------|--------|
| [QT Py ESP32-S2](https://www.adafruit.com/product/5325) | $12.50 | Excellent quality.  Easy to use with CircuitPython and WiFi. STEMMA connector makes it easy to connect the SCD-40 or 41.  Small size.
| [USB-C DATA Cable](https://amzn.to/3OW5SdE) | $10 | Includes wires for data transfer.  There are probably more inexpensive cables.  Please make sure to use one with data wires.
| [SCD-40 BoB](https://www.adafruit.com/product/5187) | $44.95 | Excellent quality.  Provides accurate CO2 readings.  STEMMA connector makes it easy to connect to the QT PY.
| [JST SH 4-Pin Cable](https://www.adafruit.com/product/4399) | $0.95 | Excellent quality. Connects the QT PY to the SCD-4x. No soldering required.
| Photoresistor | pennies | At some point I bought [a pack of photoresistors on Amazon](https://www.amazon.com/s?k=photoresistor).
| 12K  Resistor | pennies | As with photoresistors, I bought [a pack of resistors on Amazon](https://www.amazon.com/s?k=resistor).
| wiring | pennies | I like to use [silicone wires like this wire kit on Amazon](https://amzn.to/3C6chLU).
| enclosure | pennies | The design is an evolution of the wonderful [Tiny-D1 modular case for Wemos D1 mini by sumpfing](https://www.thingiverse.com/thing:4084654).  Thank you!


### 2. Print out the Enclosure
```{figure} images/snifferbuddy_on_printbed.jpg
:align: center
:height: 350

Top and Bottom Rings of the SnifferBuddy enclosure.
```

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
Use A2 as the pin to read for the photoresistor.
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
   - contains all of SnifferBuddy's code.  The code is [discussed later](_code_doc).

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
### 8. Plug In Your SnifferBuddy
At this point, we're hoping everything "just works"!  Plug in your SnifferBuddy to a 5V USB port.  If SnifferBuddy is working, there will be entries in the MQTT broker.
## Accuracy - SCD4x
Section 1 of the [SCD4x datasheet](https://sensirion.com/media/documents/48C4B7FB/6426E14D/CD_DS_SCD40_SCD41_Datasheet_D1_052023.pdf) describes the lower and upper bounds that a CO2, relative humidity, or temperature reading will range based on the SCD4x's accuracy.  A python program, `calculate_scd40_bounds.py`, calculates these offsets given a value for the SCD40.  For example, if the temperature reads 70 degrees F, the actual value can range from 68.6 to 71.4 degrees based on the accuracy.

## Adjusting Temperature and Relative Humidity Readings - SCD4x

### On-Chip Signal Compensation
A temperature offset is utilized to fine-tune the sensor's temperature and relative humidity (RH) output signals. The correlation between temperature and humidity necessitates an accurate temperature reading for a precise RH reading, given that moisture-carrying capacity of air is temperature-dependent. The [SCD4x datasheet](https://sensirion.com/media/documents/48C4B7FB/6426E14D/CD_DS_SCD40_SCD41_Datasheet_D1_052023.pdf) discusses the On-Chip Output Signal Compensation in section 3.6.  It's the way the chip compensates for temperature readings skewed due to self-heating from the sensor and nearby electronics, while also taking into account other influences like ambient temperature variations and airflow disruptions.   Initially, the temperature offset is set to 4°C to mitigate self-generated heat, with adjustable values between 0°C and 20°C to accommodate other environmental factors. Although a negative offset could technically be used if the sensor reads too cold, it's outside the recommended range.
### Adjusting temperature readings
1. Determine if a temperature offset is needed by placing an external reference temperature sensor with snifferbuddy and determine if after 24 hours.
2. If the reading is significantly outside the bounds, consider changing the temperature offset.
3. Place the SnifferBuddy and a reference temperature sensor at the place in the grow tent you wish to have SnifferBuddy hanging around. Wait 24 hours so both sensor aclimate.
## Adjusting Light ON/OFF threshold
A simple photoresistor is used to determine whether the light is on or off. CircuitPython maps photoresistor readings to values between 0 and 65535.  By default, light on happens when the photoresistor value is > 45,000.  This can be adjusted.
1. Put SnifferBuddy where you want to hang it.
2. Turn the light on. If SnifferBuddy sends readings that says the light is on, you are done.
3. If SnifferBuddy says the light is off when it is on, send a calibrate light mqtt message.  By doing so, SnifferBuddy will adjust it's light threshold.

## Debug
Sadly, it is a rare moment when something works the first time. Take a deep breath and let's get started!
### Check the Print Statements
In this scenario, the QT Py is plugged into a USB on your PC/Mac.  You have installed the [Mu editor](https://codewith.mu/), and can load and run code.py.  There are print statements that should help you determine what the problem might be.
### Check Out the MQTT Broker
Have any messages been sent?  The easiest way to check is to use a tool like [mqtt Explorer](http://mqtt-explorer.com/).  This tool does exactly what the name implies.  It allows you to explore the mqtt traffic as it whizzes by.  You can also publish messages.  Very handy.
```{figure} images/mqtt_explorer.jpg
:align: center
:height: 350

SnifferBuddy Topics on the Gus MQTT Broker
```
The first messages sent include:
1. A message to the lwt topic letting everyone know a SnifferBuddy is connected to the MQTT broker.

```
    client.publish(userdata["lwt_topic"], userdata["online_payload"], retain=True)
```
Check the configuration file for what the actual "online_payload" message is.

2. A log message sent before readings are published.

```
logger.debug("Sending Readings")
```
The logging message with be under the config['log_topic'] (default is SnifferBuddy/log).  It will look like this:
```
8.000: DEBUG - Sending Readings
```
Where:
- 8.000 is a floating point number that represents the number of seconds since boot (see [monotonic time](https://learn.adafruit.com/clue-sensor-plotter-circuitpython/time-in-circuitpython )).
- DEBUG notes this logging message to be at the debug level.
- "Sending Readings" is the message.

### Using LWT and Logging for Debugging

SnifferBuddy has set up the optional Last Will and Testament (LWT) feature of MQTT. LWT is a method to notify clients by the broker when the client ungracefully disconnects or stops sending messages.  To set up LWT, the will_set() method is called:
```
mqtt_client.will_set(config["lwt_topic"], config["offline_payload"], retain=True)
```
prior to connecting.  This sets the topic and the text for the payload of the broadcasted message when the broker detects the client is offline.

### HELP!
If you need help debugging or have other questions, please send a message.
```{button-link} https://github.com/solarslurpi/GrowBuddies/discussions
:outline:
:color: success

 {octicon}`comment;1em;sd-text-success` Comments & Questions
```
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