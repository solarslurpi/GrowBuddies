#import colors_code

(snifferbuddy_doc)=
# SnifferBuddy
:::{div}
<img src="images/dog.jpg" class="sd-avatar-md sd-border-3">
:::


## About {material-regular}`question_mark;1em;sd-text-success`
:::{div}
<img src="https://docs.google.com/drawings/d/e/2PACX-1vQnc4PqB6jgMzFOIMZqWpJ1dFUUdEsrNfNtB4n6q8jmW68PfWBYvIfANB0gqFjMqUh3rn0Cm_YLLthx/pub?w=984&amp;h=474&amp;align=middle">
:::

sniff...sniff...sniff...Inside SnifferBuddy is a [SCD30 air quality sensor](https://www.adafruit.com/product/4867) measuring the air's temperature, humidity, and CO2 level.   There is a photoresistor at the top of SnifferBuddy to indicate whether the grow lights are on or off. The brain behind SnifferBuddy is an ESP286 running [Tasmota firmware](https://tasmota.github.io/docs/About/). The Tasmota software publishes the readings over mqtt to an mqtt broker running on [Gus()](gus_doc).

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
(make_snifferbuddy)=
## Let's Make One {material-regular}`build;1em;sd-text-success`
```{note}
SnifferBuddy sends out mqtt messages in which the payload includes the sensor readings.  You can use any mqtt environment to interact with a SnifferBuddy.  If you have built [Gus](gus), Gus will know what to do with the SnifferBuddy messages.  This document assumes [Gus](gus) has been built.
```


Once plugged in and working, you will be able to (compliments of [Gus](gus)):
- Store readings into an influxdb table (referred to as a measurement influxdb terminology) influxdb.
- Visualize your readings using grafana.
### Gather The Materials

- [SCD30 sensor](https://www.adafruit.com/product/4867) component.
- [ESP8286](https://www.aliexpress.us/item/2251832645039000.html) component.
- Photoresistor and 10K through hole resistor.  I had alot of these kicking around. I bought something similar to [this kit](https://amzn.to/3yNZtZd).
- 3D printer and PLA filament for printing out [the enclosure](enclosure).
- Superglue for gluing the top Wemos part of the enclosure to the cap part of the enclosure.
- USB chord and plug the ESP8286 to power.
- 4 4mm M2.5 or M3 bolts.
(enclosure)=
### Make the Enclosure

The SnifferBuddy enclosure was designed within Fusion 360 and printed on a Prusa MK3s using PLA filament.  I use the F360  app extension [Parameter I/O](https://apps.autodesk.com/FUSION/en/Detail/Index?id=1801418194626000805&appLang=en&os=Win64) to import/export the parameters found in [SnifferBuddyParams.csv](https://github.com/solarslurpi/GrowBuddies/blob/c100124acaab285eadb284a5e7015e569ed76d3c/enclosures/SnifferBuddy/SnifferBuddyParams.csv).

To make the enclosure, download and print the ([4 mesh files](https://github.com/solarslurpi/growBuddy/tree/main/enclosures/SnifferBuddy)).
:::{figure} images/snifferbuddy_parts_on_printer_plate.jpg
:align: center
:height: 350

SnifferBuddy Enclosure Parts
:::
- [WemosD1_top.stl](https://github.com/solarslurpi/growBuddy/blob/main/enclosures/SnifferBuddy/WemosD1_top.stl)
- [WemosD1_base.3mf](https://github.com/solarslurpi/growBuddy/blob/main/enclosures/SnifferBuddy/wemosD1_base.3mf)
- [scd_cap.3mf](https://github.com/solarslurpi/growBuddy/blob/main/enclosures/SnifferBuddy/scd_cap.3mf)
- [scd30 enclosure.stl](https://github.com/solarslurpi/growBuddy/blob/main/enclosures/SnifferBuddy/scd30%20enclosure.stl)

[The directory](https://github.com/solarslurpi/growBuddy/tree/main/enclosures/SnifferBuddy) also includes the Fusion 360 files, including [a Fusion 360 file of a Wemos D1](https://github.com/solarslurpi/growBuddy/blob/main/enclosures/SnifferBuddy/_Wemos.8a6fa8fd-bdae-4608-9551-e9ac450bc9c8.f3d) for modeling.


### Wire the Components Together
The SCD30 and photoresistor are wired to an [ESP826 D1](https://i2.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/ESP8266-WeMos-D1-Mini-pinout-gpio-pin.png?quality=100&strip=all&ssl=1) mini](https://i2.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/ESP8266-WeMos-D1-Mini-pinout-gpio-pin.png?quality=100&strip=all&ssl=1).
:::{figure} images/SnifferBuddy_wiring.jpg
:align: center
:scale: 100

SnifferBuddy Wiring
:::

I settled on the ESP826 because I settled on [Tasmota](https://tasmota.github.io/docs/) as the way to send sensor readings over mqtt.
I figured if [Tasmota's goal](https://tasmota.github.io/docs/About/) was to *"provide ESP8266 based ITEAD Sonokff devices with MQTT and 'Over the Air' or OTA firmware"...*
Then why not use the same chip?   I {ref}`ran into an issue with the Wemos D1 ESP286<wemos_challenges>` when I made the first SnifferBuddy.  But for the most part, ESP826's are very
inexpensive and work.  I ordered some from [Aliexpress](https://www.aliexpress.us/item/2251832645039000.html).  I put a Photoresistor on the top as a way to determine
if the grow lights were on or off.  I use this for knowing when to go into daytime or nighttime care.

(scd30_wiring)=
#### WemosD1 to SCD30 Wiring

Thanks to vendors like [Adafruit](https://www.adafruit.com/), we have a vast amount of sensors and microcontrollers that we can connect together.  However, only a few companies (like Adafruit) include connectors on their Breakout Boards.  I like the idea of standardizing on a couple of JST connectors and discussing that more in [the wiring section](wiring_doc)

:::{figure} images/wemosd1_wiring.jpg
:align: center
:scale: 100

Wemos D1 Wiring
:::

The Photoresistor is "hard-wired" to the ESP286's analog pin.  The SCD30 is an I2C device.  Since I may want to reuse the SCD30, and I want to make the connection cleaner, I will use a JST SH connector.


### Install Tasmota
Time to install Tasmota onto the ESP8286.  See [Tasmota Installation](tasmota_installation).

#### Verify Install
You can use a tool like [mqtt explorer](mqtt_explorer) to see if SnifferBuddy is sending out mqtt messages.

(snifferbuddy_storereadings)=
## Store Readings {material-outlined}`storage;1em;sd-text-success`

### snifferbuddy_storereadings.py
```{button-link} https://github.com/solarslurpi/GrowBuddies/blob/930420abc7ddd4cf4c74c408d61819eec0968a44/growbuddies-project/growbuddies/examples/snifferbuddy_storereadings.py
:outline:
:color: success

 {octicon}`mark-github;1em;sd-text-success` View Code
```

```{eval-rst}
.. automodule:: growbuddies.examples.snifferbuddy_storereadings
   :members:
```

## About Logging {material-outlined}`description;1em;sd-text-success`

```{button-link} https://github.com/solarslurpi/GrowBuddies/blob/5942d40bff58e11be8e78d7296eb0daa9fff5a17/code/logginghandler.py
:outline:
:color: success

 {octicon}`mark-github;1em;sd-text-success` View Code
```
```{eval-rst}
.. automodule:: growbuddies.logginghandler
   :members:
```

## Plot Readings  {material-outlined}`multiline_chart;1em;sd-text-success`
```{note}
These steps assume you have already [installed Grafana on Gus](make_gus) and kept the defaults (database, hostname) to `gus`.
```

The data collected while running a Python Script - like the code discussed under the  {ref}`snifferbuddy_storereadings` topic - can be viewed within the powerful
[Grafana](https://en.wikipedia.org/wiki/Grafana) graphing package.

### Login to Grafana

```{note}
You must install Grafana on Gus() first.  For this step, see the [Make Gus()](make_gus) step.
```
[The pimylifeup web post](https://pimylifeup.com/raspberry-pi-grafana/) does an excellent job walking us through setting up Grafana login.

**Start at step 2**. You'll see the line `http://<IPADDRESS>:3000`.  Most likely you will use the URL `http://gus:3000`.

- log in to Grafana (go through steps 2 through 5)

As pimylifeup notes: _At this point, you should now have Grafana up and running on your Raspberry Pi and now be able to access its web interface._
```
http://gus:3000
```
### Connect to the Gus Database
```{note}
These steps assume you kept the defaults (database, hostname) to `gus`.
```
Now that we can log into Grafana, let's connect to the gus database.

#### Choose the Data Source

From the Grafana screen, choose to add a data source.
:::{figure} images/grafana_add_datasource.jpg
:align: center
:scale: 100

Grafana Data Source Options
:::

You'll be greeted by a list of several data source choices.  Choose `influxDB`.
#### Name the Data Source
Name the database `Gus` and toggle the Default switch to the ON position.
:::{figure} images/grafana_influxdb_data_source_name.jpg
:align: center
:scale: 100

Grafana - InfluxDB Name the Data Source
:::
#### Fill in HTTP Connection Parameters
Fill in the URL, choose Basic Auth, then provide the Basic Auth password to `gus`.

:::{figure} images/grafana_influxdb_http_config.jpg
:align: center
:scale: 50

Grafana - InfluxDB HTTP Connection Settings
:::
#### Fill in influxDB Parameters
Now fill in the influxDB parameters.

:::{figure} images/grafana_influxdb_influxdb_config.jpg
:align: center
:scale: 75

Grafana - InfluxDB InfluxDB Settings
:::
Choose Save & Test ...and...
_**Hopefully**_ you can smile looking at:
:::{figure} images/grafana_influxdb_data_test_worked.jpg
:align: center
:scale: 75

Grafana - InfluxDB Connection Success
:::
### Plot Readings
Grafana's workflow to get to looking at sensor readings includes:
#### Create a Dashboard
:::{figure} images/grafana_new_dashboard.jpg
:align: center
:scale: 75

Grafana - Create a New Dashboard
:::
#### View Readings
Create a dashboard then create a panel within the dashboard.

Now you are at what Grafana calls a Panel.  The image shows a panel set up to show vpd `SnifferBuddyReadings()`.
1. Set the Data Source to Gus.
2. Set the Table (InfluxDB calls a table a Measurement), which is the `From` field. is set to "sniff2" (recall this is the table created after running the {ref}`snifferbuddy_storereadings`.
3. Set the `Select` field to `vpd`.
4. The time was to a range that includes `SnifferBuddyReadings()`.
After setting the parameters similar to what is done in the image, you should see a plot similar to the one in the image.  There are a few differences based on configuring Grafana plot features.  They are all covered in the online Grafana documentation.

:::{figure} images/grafana_snifferbuddyreadings_vpd.jpg
:align: center
:scale: 75

Plot of SnifferBuddyReadings for vpd.
:::

The results point to an average vpd at that date/time range of about 1.3.
### Analyze Readings
Looking at [FLU's VPD Chart](https://www.canr.msu.edu/floriculture/uploads/files/Water%20VPD.pdf)
:::{figure} images/vpd_chart.jpg
:align: center
:scale: 75

Plot of SnifferBuddyReadings for vpd.
:::

```{danger}
A vpd reading of 1.3 is saying the grow environment is stressful for the plant.
```
The humidity or the temperature could be adjusted.  Here is a plot of the temperature and vpd.  While the vpd averages about 1.3, the temperature ranges between 73 and 75.  This is because my grow tent environment is in my house, which is climate controlled.  The LED lights raise the temperature a bit.  The fans cool the temperature a bit.  It's pretty ideal.  Thus, [MistBuddy](mistbuddy_doc) focuses on turning a humidifier on and off for just the right amount of time.

:::{figure} images/grafana_snifferbuddyreadings_vpd._and_temp.jpg
:align: center
:scale: 65

Plot of SnifferBuddyReadings for vpd and temperature.
:::


## Run as a Service
Running {ref}`snifferbuddy_storereadings` over ssh will stop when the desktop gets connected.  What needs to happen is to set up {ref}`snifferbuddy_storereadings` as a [Systemd service](systemd_doc).

