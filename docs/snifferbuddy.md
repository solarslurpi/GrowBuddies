

# SnifferBuddy

SnifferBuddy sniffs out values for the air temperature, CO2 level, and humidity. I also put in a photoresister on top to let me know when
the LEDs are on or off.  The readings are sent out over wifi using mqtt to the GrowBuddy broker.

Putting a SnifferBuddy together is easy. The hardest part is soldering the wires to the pins!

## Outside View
The one I made looks like this:

:::{figure} images/Sniffer_Buddy.jpg
:align: center
:height: 350

SnifferBuddy
:::

## Inside View
:::{figure} images/SnifferBuddy_wiring.jpg
:align: center
:scale: 100

SnifferBuddy Wiring
:::

The star of SnifferBuddy is the [SCD30 sensor from Adafruit](https://www.adafruit.com/product/4867) .  I had one in my parts bin.  The SCD30 is wired to  an
[ESP826 D1 mini](https://i2.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/ESP8266-WeMos-D1-Mini-pinout-gpio-pin.png?quality=100&strip=all&ssl=1).  
I settled on the ESP826 because I settled on [Tasmota](https://tasmota.github.io/docs/)  as the way to send sensor readings over mqtt.
I figured if [Tasmota's goal](https://tasmota.github.io/docs/About/) was to *"provide ESP8266 based ITEAD Sonokff devices with MQTT and 'Over the Air' or OTA firmware"...*
Then why not use the same chip?   I {ref}`ran into an issue with the Wemos D1 ESP286<flakey_wemos>` when I made the first SnifferBuddy.  But for the most part, ESP826's are very
inexpensive and work.  I ordered some from [Aliexpress](https://www.aliexpress.us/item/2251832645039000.html).  I put a Photoresistor on the top as a way to determine
if the grow lights were on or off.  I use this for knowing when to go into daytime or nightime care.


## Wiring
__[Caution...Wiring ahead..take care!](wiring)__

Wiring components together is my biggest source of frustration with projects.  Besides the confusing ugliness of my thoughtless wiring,
:::{figure} images/SnifferBuddy_innerds.jpg
:align: center
:scale: 100

SnifferBuddy Wiring
:::


The haphazard wiring is prone to lose connection or cause a short.




Based on {ref}`my reflections on wiring,<wiring>` Here's how I would wire up a SnifferBuddy:

The Photoresistor is "hard wired" to the ESP286's analog pin.  The SCD30 is an I2C device.  Since I may want to reuse the SCD30, and I want to make the connection cleaner, I will use a JST SH connector.

## Software

The ESP286 on SnifferBuddy runs [Tasmota](https://tasmota.github.io/docs/) .

### Thanks to Those That Went Before

It is amazing what we can DIY riding on the backs of the incredible insight and work by people like [Theo Arends](https://github.com/arendst) .  Tasmota is simple in one way - it is an extremely easy way to send mqtt readings from sensors attached to an ESP.  Can it get complex quickly, you bet.  Tasmota is very powerful.  And you may need to be prepared to bumble through Tasmota code to get an answer to your questions.  However, the Discord channel tends to be very helpful and there is documentation to get you started.  I say all this because, like other "programming environment", there is a culture, a way of life, associated with it.

## Enclosure

- download and print the ([4 files](https://github.com/solarslurpi/GrowBuddy/tree/main/enclosures/SnifferBuddy)).

The SnifferBuddy enclosure was designed within Fusion 360 and printed on a Prusa MK3s using PLA filament.  I use the F360  app extension [Parameter I/O](https://apps.autodesk.com/FUSION/en/Detail/Index?id=1801418194626000805&appLang=en&os=Win64) to import/export the parameters found in [SnifferBuddyParams.csv](https://github.com/solarslurpi/GrowBuddy/blob/c100124acaab285eadb284a5e7015e569ed76d3c/enclosures/SnifferBuddy/SnifferBuddyParams.csv).

:::{figure} images/snifferbuddy_enclosure.jpg
:align: center
:height: 350

SnifferBuddy Enclosure Ready for Halloween!
:::

(make-snifferbuddy)=
## Let's Make One!

- Step 1: Get the materials. See {ref}`Materials`.
- Step 2: Print out the [enclosure](enclosure).  There are three STL files.
- Step 3: {ref}`Wire <wiring>` the components together.
- Step 4: Plug the ESP286 into the USB port of your PC/Mac. __Make sure to use a USB cable that handles data i/o.__
- Step 5: Install Tasmota onto the ESP8286.  See {ref}`Tasmota Installation <tasmota_installation>`.



### Materials

- [SCD30 sensor](https://www.adafruit.com/product/4867) component. _Note: I have successfully used and SCD40 sensor.  The challenge is it is not by default in the Tasmota Sensors build.  Other sensors can be added if needed._
- [ESP8286](https://www.aliexpress.us/item/2251832645039000.html) component.
- Photoresistor and 10K through hole resistor.  I had alot of these kicking around. I bought something similar to [this kit](https://amzn.to/3yNZtZd).
- 3D printer and PLA filament for printing out the enclosure.
- Superglue for gluing the top Wemos part of the enclosure to the cap part of the enclosure.
- USB chord and to plug the ESP8286 to power.

