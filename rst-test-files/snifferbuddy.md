(snifferbuddy)=

# SnifferBuddy

SnifferBuddy sniffs out values for the air temperature, CO2 level, and humidity. I also put in a photoresiter on top to let me know when
the LEDs are on or off.  The readings are sent out over wifi using mqtt to the GrowBuddy broker.

Putting a SnifferBuddy together is easy. The hardest part is soldering the wires to the pins!

The one I made looks like this:

:::{figure} images/Sniffer_Buddy.jpg
:align: center
:height: 350

SnifferBuddy
:::

## Hardware

:::{figure} images/SnifferBuddy_wiring.jpg
:align: center
:scale: 100

SnifferBuddy Wiring
:::

The star of SnifferBuddy is the [SCD30 sensor from Adafruit](https://www.adafruit.com/product/4867) .  I had one in my parts bin.  The SCD30 is wired to  an
[ESP826 D1 mini](https://i2.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/ESP8266-WeMos-D1-Mini-pinout-gpio-pin.png?quality=100&strip=all&ssl=1) I had
in my parts bin.  I settled on the ESP826 because I settled on [Tasmota](https://tasmota.github.io/docs/)  as the way to send sensor readings over mqtt.
I figured if [tasmota's goal](https://tasmota.github.io/docs/About/) was to *"provide ESP8266 based ITEAD Sonokff devices with MQTT and 'Over the Air' or OTA firmware"...*
Then why not use the same chip?  On the one hand, I have used ESP826 microcontrollers in the past with mixed results.  On the other hand, ESP826's are very
inexpensive and work.  I ordered some from [Aliexpress](https://www.aliexpress.us/item/2251832645039000.html).  I put a Photoresistor on the top as a way to determine
if the grow lights were on or off.  I use this for knowing when to go into daytime or nightime care.

### Wiring

What a mess.  I won't even try to make a pretty image.  There is no way...I have started to  {ref}`standardize the wiring<wiring>`

:::{figure} images/SnifferBuddy_innerds.jpg
:align: center
:height: 350

SnifferBuddy Wiring
:::

What a mess.  I won't even try to make a pretty image.  There is no way... Thank goodness I am not a professional like this person.

```{image} images/wiring_pole.jpg
:align: center
:scale: 60
```

The good news is the wiring works.  Wiring is components together - like the ESP286 and the SCD30 - is probably the hardest part of working with hardware for the DIYer.  Previously, I might have built a custom PCB but that takes time and besides the folks - like Adafruit - making components really know how to surround the component with robust circuits that typically don't start on fire. *Note: I haven't had an ESP286 catch on fire, but I've had a few get really warm*

#### NEW and IMPROVED Wiring

Based on {ref}`my reflections on wiring,<wiring>` Here's how I would wire up a SnifferBuddy:

The Photoresistor is "hard wired" to the ESP286's analog pin.  The SCD30 is an I2C device.  Since I may want to reuse the SCD30, and I want to make the connection cleaner, I will use a JST SH connector.

## Software

The ESP286 on SnifferBuddy runs [Tasmota](https://tasmota.github.io/docs/) .

### Thanks to Those That Went Before

It is amazing what we can DIY riding on the backs of the incredible insight and work by people like [Theo Arends](https://github.com/arendst) .  Tasmota is simple in one way - it is an extremely easy way to send mqtt readings from sensors attached to an ESP.  Can it get complex quickly, you bet.  Tasmota is very powerful.  And you may need to be prepared to bumble through Tasmota code to get an answer to your questions.  However, the Discord channel tends to be very helpful and there is documentation to get you started.  I say all this because, like other "programming environment", there is a culture, a way of life, associated with it.

## Enclosure

The [SnifferBuddy enclosure](https://github.com/solarslurpi/GrowBuddy/tree/main/enclosures/SnifferBuddy) was designed within Fusion 360 and printed on a Prusa MK3s using PLA filament.  I use the F360  app extension [Parameter I/O](https://apps.autodesk.com/FUSION/en/Detail/Index?id=1801418194626000805&appLang=en&os=Win64) to import/export the parameters found in . [SnifferBuddyParams.csv](https://github.com/solarslurpi/GrowBuddy/blob/c100124acaab285eadb284a5e7015e569ed76d3c/enclosures/SnifferBuddy/SnifferBuddyParams.csv)

## Let's Make One!

- Step 1: Get the materials. See {ref}`Materials`.
- Step 2: Install Tasmota onto the ESP8286.  See {ref}`Tasmota`.
- Step 3: Wire the components together.

(materials)=

### Materials

- [SCD30 sensor](https://www.adafruit.com/product/4867) component.
- [ESP8286](https://www.aliexpress.us/item/2251832645039000.html) component.
- Photoresistor and 10K through hole resistor component.
- Print out the [case top](https://github.com/solarslurpi/GrowBuddy/blob/main/enclosures/SnifferBuddy/base%20and%20lid%20v14.f3d).
- print out the SCD30 enclosure [(case bottom)](https://github.com/solarslurpi/GrowBuddy/blob/main/enclosures/SnifferBuddy/scd30%20enclosure%20v1.f3d).
- USB chord to plug the ESP8286 to power.
- USB power hub to plug the USB chord into the wall.
