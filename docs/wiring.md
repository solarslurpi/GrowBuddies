(wiring)=

# Wiring Components Together

Wiring components together is a big source of frustration.

:::{figure} images/wiring_pole.jpg
:align: center
:height: 350

What a Mess!
:::


It has been many a time my haphazard wiring has lost the connection or caused a short.  I decided to stick to a few commonly used connectors.

## Connectors - Just Pick One

I like the direction companies like Adafruit are going by standardizing on a specific connection.  I am picking up Adafruit's  [stemma](https://learn.adafruit.com/introducing-adafruit-stemma-qt)  style of connecting components.
- STEMMA connectors are 3 or 4 pin JST PH connectors.  The pins of these connectors are 2mm apart (i.e.: 2mm pitch)
- STEMMA QT connectors are 3 or 4 pin JST SH connectors.  These connectors are quite small.  The pins are at a 1mm pitch.

For some reason, I found JST connectors confusing.  I oddly found some relief to find out I'm not alone in my confusion.

### Awesome Articles on JST

- Why JST "connectors" gets complicated and the importance of thinking about connectors up front: [JST IS NOT A CONNECTOR](https://hackaday.com/2017/12/27/jst-is-not-a-connector/) .
- One man's voyage through the JST jungle:  [JST Connector Crimping Insanity](https://iotexpert.com/jst-connector-crimping-insanity/) .


## Wiring growBuddy Components Together

I ended up getting pre-crimped JST PH (2mm between pins...small but not that small) and SH (1 mm between pins.. smallest).  I noticed at least one of the comments expressed outrage in the high price and we should just all crimp the wires ourselves.  I guess we could.  But it would take too much practice so in my equation, the extra money was well worth the time savings.
- [pre-crimped STEMMA/JST PH 2.0 cable kit](https://amzn.to/3SLurIX) from Amazon.
- [Pre-crimped STEMMA QT/JST PH 1.0 cable kit](https://amzn.to/3MyOCrV) from Amazon.


### STEMMA QT/JST PH 1.0 Wiring Example

Here's a wiring of a soil moisture sensor I recently did.

```{image} images/soil_moisture.jpg
:align: center
:scale: 60
```

The enclosure has a connector area to place the JST connector.
