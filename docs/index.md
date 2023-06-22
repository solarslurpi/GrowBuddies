% growBuddy documentation master file, created by
% sphinx-quickstart on Mon Sep 26 14:48:47 2022.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Welcome to GrowBuddies! {material-regular}`yard;2em;sd-text-success`

```{mermaid}

sequenceDiagram
   participant Alice
   participant Bob
   Alice->John: Hello John, how are you?
```



GrowBuddies is a bunch of DIY devices for geeky gardeners. They work together to maximize the yield while minimizing the guesswork.
```{note} Currently, knowledge of Python is required.  It also doesn't hurt to know how to solder. It would be wonderful if you would share your thoughts on how GrowBuddies can improve.

```{button-link} https://github.com/solarslurpi/GrowBuddies/issues
:ref-type: myst
:align: center
:color: success
:shadow:
Leave a Comment
```

```
## SnifferBuddy
The core device is SnifferBuddy. SnifferBuddy tracks light, temperature, humidity, CO2, and calculates VPD, sending readings through MQTT over WiFi.

```{figure} images/snifferbuddy_in_tent.jpg
:align: center
:scale: 60

SnifferBuddy Monitors Temps, RH, CO2, VPD, and Light Level
```
It's compatible with MQTT ecosystems like node-red or AdafruitIO.


```{button-link} snifferbuddy.md
:ref-type: myst
:align: center
:color: success
:shadow:
Let's Make One
```

## Gus
Another option to process SnifferBuddy's MQTT messages is to build Gus.  Gus is a Raspberry Pi 3/4, running the Mosquitto MQTT broker.

```{figure} images/Gus_2.jpg
:align: center
:scale: 60

A Rasp Pi 3 Gus and a Rasp Pi 4 Gus
```


 Gus:
 - runs on a Raspberry Pi.
 - uses the local wifi.
 - is an MQTT Broker that can respond to GrowBuddies' MQTT messages.
 - can store SnifferBuddy readings in an influxdb database.
 - can plot the SnifferBuddy readings in Grafana.
 - can manage an "ideal" vpd setpoint.
 - can manage a CO2 level setpoint.

 For example, the powerful Grafana graphing package is freely available on the Raspberry Pi.  We can use it to plot SnifferBuddy values that were stored within an influxdb table.


```{figure} images/co2andvpdvalues.jpg
:align: center
:scale: 60

Grafana Plots SnifferBuddy Data on Gus
```
Here we see the plot of CO2 (purple) and vpd (green).  It shows the vpd is staying around its setpoint of 1.0.  The CO2 is slowly rising to between 750 and 800 ppm.

```{button-link} gus.md
:ref-type: myst
:align: center
:color: success
:shadow:
Let's Make One
```
## MistBuddy
MistBuddy maintains a grow tent's ideal [vpd level](https://www.canr.msu.edu/floriculture/uploads/files/Water%20VPD.pdf).   When the vpd level is too high, MistBuddy spouts out mist to raise the vpd level to maintain a vpd setpoint value.  When the vpd is too low or just right compared with the setpoint, MistBuddy shuts off until the vpd level is higher than the vpd setpoint.

```{note} Most indoor grow environments are climate controlled.  Typically, the temperature is within acceptable range however the humidity is not.  Because of this, while vpd is dependent on both temperature and humidity, MistBuddy only changes the humidity to adjust the vpd.
```
```{button-link} mistbuddy.md
:ref-type: myst
:align: center
:color: success
:shadow:
Let's Make One
```



```{eval-rst}
.. toctree::
   :maxdepth: 2

   growbuddies
   store_readings
   manage_vpd
```