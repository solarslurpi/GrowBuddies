(mistbuddy_doc)=
# MistBuddy

MistBuddy in Action:

:::::{grid} 10

::::{grid-item}
:columns: 2

::::

::::{grid-item}
:columns: 6

:::{card}
:img-background: images/MistBuddy_misting.jpg
:::

::::
:::::

If you squint closely at the upper left of the grow tent you can see mist puffing out of the long PVC.  That's MistBuddy doing it's thing.

MistBuddy has a whale of a good time maintaining a grow tent's ideal [vpd level](https://www.canr.msu.edu/floriculture/uploads/files/Water%20VPD.pdf).   When the vpd level is too high, MistBuddy spouts out mist for **just** the right amount of time.  When the vpd is too low or just right, MistBuddy shuts off until the vpd level is higher than the vpd level setpoint.  Our indoor gardening environment is climate controlled.  The temperature with the LED lights stays at a stress free level of between 75&#8457; and 85&#8457;.  While vpd is dependent on both temperature and humidity, MistBuddy only changes the humidity to adjust the vpd.

```{note} MistBuddy presumes there is a working [Gus](gus) and [SnifferBuddy](snifferbuddy) on the same WiFi.
```
::::{grid} 2 2 2 2

:::{grid-item}
:columns: 2
:::

:::{grid-item}
:columns: 4
```{button-ref} make_snifferbuddy
:ref-type: myst
:align: center
:color: success
:shadow:
Make SnifferBuddy
```
:::
:::{grid-item}
:columns: 4
```{button-ref} make_gus
:ref-type: myst
:align: center
:color: success
:shadow:
Make Gus
```
:::
::::
## Glossary
(_vpd)=
**VPD** - Vapor Pressure Deficit (VPD) is a measure of the difference between the actual and saturation water vapor pressure at a certain temperature. It directly influences a plant's rate of transpiration.  High VPD results in increased transpiration, leading to potential plant stress from excessive water loss. This can manifest as wilted leaves, slowed growth, reduced crop yield, and in extreme cases, plants dry up and die.  High VPD conditions can deter certain pests preferring moist environments but can encourage others like spider mites and thrips that thrive in hot, dry conditions.  Low VPD can lead to reduced transpiration, affecting nutrient transport within the plant and causing lower rates of photosynthesis due to stomatal closure. This condition also increases the risk of diseases such as powdery mildew and botrytis, as well as other pathogens that thrive in high humidity.

Different plant types will prefer different ideal vpd levels.  Some plants, like cacti and other succulents, are adapted to arid environments with potentially high VPD levels. They have evolved various mechanisms to conserve water, such as reduced leaf surface area and the ability to store water in their tissues.  On the other hand, plants native to humid, tropical environments, like orchids, may prefer lower VPD levels. These plants have evolved to thrive in conditions of high humidity and are typically more sensitive to water loss through transpiration.

I found this [YouTube video best explained (at least to the way I see things) water vapor, temperature's relationship to Relative Humidity and VPD](https://www.youtube.com/watch?v=-bYPGr1TJQY&t=1s).

**Tasmota/Tasmotized** - **Tasmota** is an open-source firmware developed for ESP8266 and ESP32 devices. These devices include things like smart plugs, light bulbs, and other Internet of Things (IoT) devices. It is designed to offer local control of your devices. The Tasmota GitHub provides [a list of Tasmota devices](https://templates.blakadder.com/)

The term **"Tasmotized"** is often used in the hobbyist community to refer to a device that has been flashed or reprogrammed with the Tasmota firmware. This is often done to extend the capabilities of the device or to make it compatible with a wider range of home automation software.
(_make_mistbuddy)=
## Make MistBuddy
MistBuddy consists of a humidifier and two Tasmotized smart plugs.
### HUMIDIFIER
The humidifier is an evolution of the one in the YouTube video _[How to Build a Homemade Humidifier Using Ultrasonic Misters / fogger](https://www.youtube.com/watch?v=vmiO6Z_HLCE)_.
#### Get the parts together

  The supplies needed to build this component of MistBuddy include:

| Component | Cost | Reason |
|-----------|------|--------|
| Storage Tote |$10.50 | I used this [Storage Tote from Home Depot](https://www.homedepot.com/p/HDX-14-Gal-Tough-Storage-Tote-in-Black-with-Yellow-Lid-SW111/314468098).
| 2" PVC Pipe | $16 | Another [Home Depot purchase](https://www.homedepot.com/p/Charlotte-Pipe-2-in-x-10-ft-PVC-Schedule-40-DWV-Pipe-PVC-07200-0600/100348475).
| 2" PVC 90° elbow| $2.60  | [Home Depot](https://www.homedepot.com/p/Charlotte-Pipe-2-in-PVC-DWV-90-Degree-Hub-x-Hub-Elbow-PVC003001000HD/203393418).
| Waterproof IP67 12v Fan | $18 | I got [this fan from Amazon](https://amzn.to/3WgADKK).  It is powerful and waterproof.  It also has a nice, solid connector connecting the power source to the fan.
| Power source for the fan | $8 | [This is a very compact power source](https://amzn.to/3VT9pKp) that has the right connector to connect the fan.
| Mist maker | $34.10 | I bought the [Mist maker I use from Aliexpress](https://www.aliexpress.com/item/3256803543458943.html?spm=a2g0o.order_list.0.0.57dd1802LzMQr6).  I did not do any measurements to determine the ideal amount of misters.  Perhaps less can be used.
| Power source for the mist maker. | $40 | The  [Aliexpress listing](https://www.aliexpress.us/item/3256803543458943.html) notes a power source of 350W and 48V is needed.  I have an old power supply that is less powerful than this that works fine.
| Float Valve | $10 | [Float Valve](https://amzn.to/43NemIL) to stop the constantly running water line from filling the tub.
| Water Source Connector | $15 (for 4) | [1/2" Barb to 1/2 " NPT female connector](https://amzn.to/3yzxlsG) _Note: The _connector fittings _assume_ 1/2"_ PEX connector to incoming water_ (see image below)

<!-- 2 cols for xtra small, 3 for small, 3 for medium, and 3 for large screens -->

:::::{grid} 10

::::{grid-item}
:columns: 2

::::

::::{grid-item}
:columns: 3

:::{card}
:img-background: images/float_valve_connector.jpg
:::
Float Valve Connection
::::

::::{grid-item}
:columns: 3

:::{card}
:img-background: images/power__supply.jpeg
:::
Power Supply
::::

:::::

#### Make the Humidifier
Mistbuddy dispenses vapor at the end of the PVC tube by turning on a multi-head mister.  Water comes into the tub through a connection with our house's plumbing.  The water is kept to a constant level in the tub by a float valve.

:::::{grid} 12

::::{grid-item}
:columns: 2
::::

::::{grid-item}
:columns: 4

:::{card}
:img-background: images/MistBuddy.jpeg
:::
Assembled Components
::::

::::{grid-item}
:columns: 4

:::{card}
:img-background: images/MistBuddy_inside.jpeg
:::
Base and Continuous Fill
::::


:::::

Get the popcorn ... it's time for a [How To YouTube Video on making a DIY Humidifier](https://www.youtube.com/watch?v=vmiO6Z_HLCE).

The water level for the float valve is 1 cm above the sensor line.
:::::{grid} 12

::::{grid-item}
:columns: 3
::::

::::{grid-item}
:columns: 4

:::{card}
:img-background: images/mister_water_level.jpg
:::
Mister Water Level
::::

:::::

### Tasmotized Smart Plugs
[Tasmota](https://tasmota.github.io/docs/) has enabled us to build low-cost sensor and camera devices that primarily use MQTT to transmit sensor readings.  Certain Smart Plugs work with Tasmota.  MistBuddy relies on two Smart Plugs that will listen for MQTT messages from MistBuddy.  This way, the fan and the power supply of the humidifier can be turned off and on.
#### Get the parts together
| Component | Cost | Reason |
|-----------|------|--------|
| Sonoff Plugs |$30 for 4 | Two [Sonoff S31 plugs](https://amzn.to/3xnPWYc).

:::::{grid} 12


::::{grid-item}
:columns: 3
::::


::::{grid-item}
:columns: 4

:::{card}
:img-background: images/sonoff_plugs.jpg
:::
Sonoff Plugs
::::

:::::

## 4. Make Tasmotized Plugs
The MistBuddy Python code sends mqtt messages to the mister and fan plugs.  The plugs run Tasmota which handles all the mqtt messages.  Two [Sonoff S31 plugs](https://amzn.to/3xnPWYc) need to be [flashed with Tasmota](_install_mistbuddy_smartplugs).  Alternatively, find two already Tasmotized plugs that can connect to a local mqtt broker.

## Code Documentation

The general MistBuddy flow is:
- a Python script like manage_vpd sets up MQTT and callbacks to receive SnifferBuddy messages.
- The SnifferBuddy MQTT message comes in.  The Python script's callback receives the SnifferBuddy readings.
```{eval-rst}
.. autoclass:: growbuddies.mistbuddy_code.MistBuddy
   :members: __init__, adjust_humidity, turn_on_mistBuddy, turn_off_mistBuddy


```


