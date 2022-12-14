% growBuddy documentation master file, created by
% sphinx-quickstart on Mon Sep 26 14:48:47 2022.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Welcome to GrowBuddies! {material-regular}`yard;2em;sd-text-success`
Hello, fellow indoor gardeners!

The GrowBuddies project is designed to help geeky gardeners like us maximize the health and enjoyment of our indoor gardens.

Not only do GrowBuddies make gardening easier and more fun, but they also help ensure that your plants are healthy and happy. Whether you're a seasoned green thumb or just starting, GrowBuddies are the perfect partner for your indoor garden.

Stay tuned for more updates. In the meantime, happy gardening!


# Just a bunch of Buddies
 The Buddies are a team of smart and interactive companions that are here to help you optimize the growth and health of your indoor plants.  The current Buddies include:

::::{grid} 3
:gutter: 1

:::{grid-item-card} Gus
:link: gus
:link-type: doc
```{image} images/hamster.jpg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
Collect, Store, Analyze Data
:::

:::{grid-item-card} SnifferBuddy
:link: snifferbuddy
:link-type: doc

```{image} images/dog.jpg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
Uses an Air Quality Sensor to send readings over MQTT
:::

:::{grid-item-card} MistBuddy
:link: mistbuddy
:link-type: doc
```{image} images/whale.svg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
Uses SnifferBuddy Readings to Maintain the Ideal vpd
:::

::::
:::{div} sd-font-weight-bold sd-text-success
They would LOVE to be your friend!
:::





```{button-link} https://github.com/solarslurpi/GrowBuddies/discussions
:outline:
:color: success

 {octicon}`comment;1em;sd-text-success` Comments & Questions
```

## Play Time
In the bottom left-hand corner of the image, you see my grow tent.  There is a SnifferBuddy approximately in the middle of the grow tent.  It is plugged into a power port through the pink USB cable.  If you look closely, you can see a plume of mist coming out of MistBuddy.  Perfect timing for a Glamour shot.
:::{div}
<img src="https://docs.google.com/drawings/d/e/2PACX-1vTjks0iZHIZyD4VEdOo01_se0jn_CgJu9JUCee-rUhXBmFfykmObBkpqSUFBkOvnIdisiIzygPvDeZa/pub?w=984&amp;h=474&amp;align=middle">
:::
The Buddies sure love to play!  It's non-stop fun as:
- {doc}`Gus() <gus>` has set up an [mqtt broker](http://www.steves-internet-guide.com/mqtt-works/) that holds the latest SnifferBuddy readings within the mqtt message's payload.  If instructed to do so, {doc}`Gus() <gus>` can store the SnifferBuddy readings in an influxdb database.  If the readings are stored, you no longer need {doc}`Gus() <gus>` to access the readings.  For example, you can create simple to sophisticated dashboards using Grafana.  Or look at the data through apps that speak to influxdb's API.
- {doc}` SnifferBuddy <snifferbuddy>` happily puffs out [mqtt messages](mqtt_install) over a home's wifi containing air readings detected by its [SCD-30 sensor](https://www.adafruit.com/product/4867
- {doc}` MistBuddy <mistbuddy>` is an add-on that subscribes to the SnifferBuddy messages.  MistBuddy can operate in one of two modes.
    - **Observation** - MistBuddy receives SnifferBuddy messages.  You can ask for the latest vpd value, as well as the number of seconds MistBuddy calculated the MistBuddy's humidifier to turn on.
    - **Maintenance** - Does everything **Observation** does.  Adds turning on MistBuddy's humidifier for the number of seconds the vpd calculations determined.

:::{div}  sd-font-weight-bold sd-text-success
See you in the garden. {fa}`leaf;sd-text-success`
:::

```{eval-rst}
.. toctree::
   :maxdepth: 1

   getting_started
   gus
   snifferbuddy
   mistbuddy
   tasmota
   systemd
```