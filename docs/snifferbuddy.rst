************
SnifferBuddy
************

Sends out an mqtt message to the GrowBuddy broker with values for the air temperature, CO2 level, humidity readings, 
and whether the lights are on or off.

Device
######

The one I made looks like this:

.. image:: images/Sniffer_Buddy.jpg
    :width: 400
    :alt: Alternate text

Hardware
**********
-  `SCD30 sensor from Adafruit <https://www.adafruit.com/product/4867>`_ 
-  `ESP826 D1 mini <https://i2.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/ESP8266-WeMos-D1-Mini-pinout-gpio-pin.png?quality=100&strip=all&ssl=1>`_ I had in my parts bin.
-   Photoresistor and 10K resistor for light on/off detection.  I also had these parts in my parts bin.

Enclosure
*********
The enclosure was designed within F360 and printed on a Prusa MK3s.  Files within the enclosure folder include:

-  `GrowBuddyParams.csv <https://github.com/solarslurpi/GrowBuddy/blob/main/enclosure/GrowBuddyParams.csv>`_ : settings imported into F360.
-  `Fusion 360 and 3mf files <https://github.com/solarslurpi/GrowBuddy/tree/main/enclosure>`_ 
