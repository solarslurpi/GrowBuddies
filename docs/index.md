% growBuddy documentation master file, created by
% sphinx-quickstart on Mon Sep 26 14:48:47 2022.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Welcome to GrowBuddies! {material-regular}`yard;2em;sd-text-success`

Hello! Thank you for stopping by.  The GrowBuddies project is yet another Open DIY indoor gardening project.  This project's main goal is to have more fun gardening by buddying up with technology that can help us have a happier gardening experience. We get by with a little help from our Buddies...

# Just a bunch of Buddies
 The Buddies are here to help optimize the outcome of your indoor plants' growth.  The current Buddies include:

::::{grid} 3
:gutter: 1

:::{grid-item-card} Gus
:link: gus
:link-type: doc
```{image} images/hamster.jpg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
The Heavy Lifter.
:::

:::{grid-item-card} SnifferBuddy
:link: snifferbuddy
:link-type: doc

```{image} images/dog.jpg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
Sniffs out temperature, humidity, and CO2.
:::

:::{grid-item-card} MistBuddy
:link: mistbuddy
:link-type: doc
```{image} images/whale.svg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
Maintains the vpd Level.
:::

::::
:::{div} sd-font-weight-bold sd-text-success
They would LOVE to be your friend!
:::




```{note} Please [Contact me](mailto:happygrowbuddy@gmail.com) (happygrowbuddy@gmail.com) with thoughts, questions, interests.
```





## Play Time
In the bottom left hand corner of the image, you see my growtent.  There is a SnifferBuddy approximately in the middle of the grow tent.  It is plugged into a power port through the pink USB cable.  If you look closely, you can see a plume of mist coming out of MistBuddy.  Perfect timing for a Glamour shot.
:::{div}
<img src="https://docs.google.com/drawings/d/e/2PACX-1vTjks0iZHIZyD4VEdOo01_se0jn_CgJu9JUCee-rUhXBmFfykmObBkpqSUFBkOvnIdisiIzygPvDeZa/pub?w=984&amp;h=474&amp;align=middle">
:::
The Buddies sure love to play!  It's non-stop fun as:
- Good 'ol `{doc}Gus <gus>_` has set up a listening "box" [aka the mosquitto mqtt broker](http://www.steves-internet-guide.com/mqtt-works/) that holds the latest SnifferBuddy mqtt message.  If instructed to do so, Gus can store the SnifferBuddy readings in an influxdb database.  If the readings are stored, you no longer need Gus to access the readings.  For example, you can create simple to sophisticated dashboards using Grafana.  Or look at the data through apps that speak to influxdb's API.
- `{doc}SnifferBuddy <snifferbuddy>_` happily puffs out [mqtt messages](mqtt_install) over a home's wifi containing air readings detected by it's [SCD-30 sensor](https://www.adafruit.com/product/4867).

- [MistBuddy](mistbuddy) is an add-on that subscribes to the SnifferBuddy messages.  MistBuddy can operate in one of two modes.
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
   mistbuddy
   snifferbuddy
   tasmota
   systemd
```