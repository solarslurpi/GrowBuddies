


(SnifferBuddy_page)=
# SnifferBuddy
:::{div}
<img src="images/dog.jpg" class="sd-avatar-md sd-border-3">
:::


## About
sniff...sniff...sniff...SnifferBuddy happily hangs around in a grow tent sending out mqtt messages over a home's wifi.  The message payload contains readings for the air's CO2 level, relative humidity, and temperature.  There is a photoresistor at the top of SnifferBuddy to indicate whether the grow lights are on or off. The messages are sent to the growBuddy broker. This is an  mqtt broker that runs on the growBuddy server.   The star of SnifferBuddye is the [SCD30 sensor from Adafruit](https://www.adafruit.com/product/4867) . The sensor is what provides the temperature, RH, and CO2 values.  SnifferBuddy talks with the other Buddies using mqtt which is provided by [Tasmota firmware](https://tasmota.github.io/docs/About/).  The mqtt messages must be picked up by the growBuddy broker to be useful.

:::{figure} images/snifferbuddy_in_growtent.jpg
:align: center
:height: 350

A Happy SnifferBuddy hanging about
:::

The one I made looks like this:

:::{figure} images/snifferbuddy_real.jpg
:align: center
:height: 350

SnifferBuddy
:::
## Let's Make One!
At the end of these steps you will have:
- built SnifferBuddy.
- built the Base version of Gus.  Building and using Miha is optional and not included here.

Once plugged in and working, you will be able to (compliments of Gus):
- Store readings into an influxdb table (referred to as a measurement within influxdb terminology) influxdb.
- Visualize your readings using grafana.

### Get the Materials

- [SCD30 sensor](https://www.adafruit.com/product/4867) component. _Note: I have successfully used and SCD40 sensor.  The challenge is it is not by default in the Tasmota Sensors build.  Other sensors can be added if needed. It takes mucking around in the code._
- [ESP8286](https://www.aliexpress.us/item/2251832645039000.html) component.
- Photoresistor and 10K through hole resistor.  I had alot of these kicking around. I bought something similar to [this kit](https://amzn.to/3yNZtZd).
- 3D printer and PLA filament for printing out [the enclosure](enclosure).
- Superglue for gluing the top Wemos part of the enclosure to the cap part of the enclosure.
- USB chord and to plug the ESP8286 to power.
- 4 4mm M2.5 or M3 bolts.


### Make the Enclosure

The SnifferBuddy enclosure was designed within Fusion 360 and printed on a Prusa MK3s using PLA filament.  I use the F360  app extension [Parameter I/O](https://apps.autodesk.com/FUSION/en/Detail/Index?id=1801418194626000805&appLang=en&os=Win64) to import/export the parameters found in [SnifferBuddyParams.csv](https://github.com/solarslurpi/growBuddy/blob/c100124acaab285eadb284a5e7015e569ed76d3c/enclosures/SnifferBuddy/SnifferBuddyParams.csv).

To make the enclosure, download and print the ([4 mesh files](https://github.com/solarslurpi/growBuddy/tree/main/enclosures/SnifferBuddy)).
- [WemosD1_top.stl](https://github.com/solarslurpi/growBuddy/blob/main/enclosures/SnifferBuddy/WemosD1_top.stl)
- [WemosD1_base.3mf](https://github.com/solarslurpi/growBuddy/blob/main/enclosures/SnifferBuddy/wemosD1_base.3mf)
- [scd_cap.3mf](https://github.com/solarslurpi/growBuddy/blob/main/enclosures/SnifferBuddy/scd_cap.3mf)
- [scd30 enclosure.stl](https://github.com/solarslurpi/growBuddy/blob/main/enclosures/SnifferBuddy/scd30%20enclosure.stl)

[The directory](https://github.com/solarslurpi/growBuddy/tree/main/enclosures/SnifferBuddy) also includes the Fusion 360 files, including [a Fusion 360 file of a Wemos D1](https://github.com/solarslurpi/growBuddy/blob/main/enclosures/SnifferBuddy/_Wemos.8a6fa8fd-bdae-4608-9551-e9ac450bc9c8.f3d) for modeling.

:::{figure} images/SnifferBuddy_parts_on_printer_plate.jpg
:align: center
:height: 350

SnifferBuddy Enclosure Parts
:::

### Wire the Components Together
The SCD30 and photoresistor are wired to  an [ESP826 D1 mini](https://i2.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/ESP8266-WeMos-D1-Mini-pinout-gpio-pin.png?quality=100&strip=all&ssl=1).
:::{figure} images/SnifferBuddy_wiring.jpg
:align: center
:scale: 100

SnifferBuddy Wiring
:::

test [build a growBuddy server](growbuddyserver_install).

I settled on the ESP826 because I settled on [Tasmota](https://tasmota.github.io/docs/)  as the way to send sensor readings over mqtt.
I figured if [Tasmota's goal](https://tasmota.github.io/docs/About/) was to *"provide ESP8266 based ITEAD Sonokff devices with MQTT and 'Over the Air' or OTA firmware"...*
Then why not use the same chip?   I {ref}`ran into an issue with the Wemos D1 ESP286<wemos_challenges>` when I made the first SnifferBuddy.  But for the most part, ESP826's are very
inexpensive and work.  I ordered some from [Aliexpress](https://www.aliexpress.us/item/2251832645039000.html).  I put a Photoresistor on the top as a way to determine
if the grow lights were on or off.  I use this for knowing when to go into daytime or nightime care.

(scd30_wiring)=
#### WemosD1 to SCD30 Wiring

Thanks to vendors like [Adafruit](https://www.adafruit.com/), we have a vast amount of sensors and microcontrollers that we can connect together.  However, only a few companies (like Adafruit) include connectors on their Breakout Boards.  I like the idea of standardizing on a couple of JST connectors and discuss that more in [the wiring section](wiring)

:::{figure} images/wemosd1_wiring.jpg
:align: center
:scale: 100

Wemos D1 Wiring
:::

The Photoresistor is "hard wired" to the ESP286's analog pin.  The SCD30 is an I2C device.  Since I may want to reuse the SCD30, and I want to make the connection cleaner, I will use a JST SH connector.


### Install Tasmota
Time to install Tasmota onto the ESP8286.  See [Tasmota Installation](tasmota_installation).

### Build Gus
We need Gus before we can store and graph temperature, humidity, CO2, and vpd readings.  Follow [Gus's install steps](make_gus)
- Step 6: Make a growBuddyServer with mqtt and influxdb support.
<!-- ## Software

The ESP286 on SnifferBuddy runs [Tasmota](https://tasmota.github.io/docs/) .

### Thanks to Those That Went Before

It is amazing what we can DIY riding on the backs of the incredible insight and work by people like [Theo Arends](https://github.com/arendst) .  Tasmota is simple in one way - it is an extremely easy way to send mqtt readings from sensors attached to an ESP.  Can it get complex quickly, you bet.  Tasmota is very powerful.  And you may need to be prepared to bumble through Tasmota code to get an answer to your questions.  However, the Discord channel tends to be very helpful and there is documentation to get you started. -->





