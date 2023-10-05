% growBuddy documentation master file, created by
% sphinx-quickstart on Mon Sep 26 14:48:47 2022.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Welcome to GrowBuddies! {material-regular}`yard;2em;sd-text-success`

GrowBuddies are wifi enabled DIY devices and services that manage the vpd and CO2 levels in a grow tent.
(following the diagram)
1) One or more **SnifferBuddies** publish CO2, temperature, relative humidity, and calculated vpd values over MQTT.
2) The **ClimateRegulator** service running on **Gus**, a Raspberry Pi server:
- Maintains a running window of readings.  SnifferBuddy readings are coded to be sent over MQTT every 20 seconds.  However, sometimes one or more messages get back up and are sent at once, or each SnifferBuddy is getting a slightly different reading (e.g.: for temperature), or the microclimates within the grow tent cause different readings.  For whatever reason, the code in the ClimateRegulator service subscribes to SnifferBuddy MQTT messages containing the sensor values.  When a message comes in, the ClimateRegulator places it within a running window in which an average is determined. The size of the running window is determined from a property in the `growBuddies_settings.json` file.

The GrowBuddies include:
- **SnifferBuddy**: Monitors the temperature, relative humidity, CO2, and calculates VPD.  These values are sent over wifi using the popular MQTT protocol.

```{figure} images/snifferbuddy_in_tent.jpg
:align: center
:scale: 40

SnifferBuddy Monitors Temps, RH, CO2, VPD, and Light Level
```
- **MistBuddy**: Takes the SnifferBuddy readings and uses a PID controller to determine how many seconds to turn it's humidifier on.  Once MistBuddy figures out how many seconds to turn on the humidifier, it sends MQTT messages to two MQTT capable power  plugs - one to turn on the mister, the other to turn on the fan.  After the number of seconds have passed, MistBuddy sends MQTT messages to turn off the MQTT capable power plugs.
```{figure} images/MistBuddy_misting.jpg
:align: center
:scale: 40

If you squint closely at the upper left of the grow tent you can see mist puffing out of the long PVC.
```
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
   code
   PID_tuning

```