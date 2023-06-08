% growBuddy documentation master file, created by
% sphinx-quickstart on Mon Sep 26 14:48:47 2022.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Welcome to GrowBuddies! {material-regular}`yard;2em;sd-text-success`
GrowBuddies is a bunch of DIY devices for geeky gardeners. They work together to maximize the yield while minimizing the guesswork.
## SnifferBuddy
The core device is SnifferBuddy. SnifferBuddy tracks light, temperature, humidity, CO2, and calculates VPD, sending readings through MQTT over WiFi.

```{figure} images/snifferbuddy_in_tent.jpg
:align: center
:scale: 60

SnifferBuddy Monitors Temps, RH, CO2, VPD, and Light Level
```
It's compatible with MQTT ecosystems like node-red or AdafruitIO.


```{button-ref} snifferbuddy.md
:ref-type: myst
:align: center
:color: success
:shadow:
Let's Make One {material-regular}`build;1em;sd-text-white`
```

## Gus
Another option to process SnifferBuddy's MQTT messages is to build Gus.  Gus is a Raspberry Pi 3/4, running the Mosquitto MQTT broker.

```{figure} images/Gus_2.jpg
:align: center
:scale: 60

A Rasp Pi 3 Gus and a Rasp Pi 4 Gus
```
 Gus can:
 - receive and stores SnifferBuddy's MQTT messages in an influxdb database.
 - plot MQTT messages within Grafana.
 - manage an "ideal" vpd setpoint.
 - manage a CO2 level setpoint.

 For example, the powerful Grafana graphing package is freely available on the Raspberry Pi.  We can use it to plot SnifferBuddy values that were stored within an influxdb table.


```{figure} images/co2andvpdvalues.jpg
:align: center
:scale: 60

Grafana Plots SnifferBuddy Data on Gus
```
Here we see the plot of CO2 (purple) and vpd (green).  It shows the vpd is staying around its setpoint of 1.0.  The CO2 is slowly rising to between 750 and 800 ppm.
```{eval-rst}
.. toctree::
   :maxdepth: 2

   snifferbuddy
   gus
```