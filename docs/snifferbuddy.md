
(snifferbuddy_doc)=
# SnifferBuddy
:::{div}
<img src="images/dog.jpg" class="sd-avatar-md sd-border-3">
:::


## About {material-regular}`question_mark;1em;sd-text-success`
:::{div}
<img src="https://docs.google.com/drawings/d/e/2PACX-1vQnc4PqB6jgMzFOIMZqWpJ1dFUUdEsrNfNtB4n6q8jmW68PfWBYvIfANB0gqFjMqUh3rn0Cm_YLLthx/pub?w=984&amp;h=474&amp;align=middle">
:::

sniff...sniff...sniff...Inside SnifferBuddy is a [SCD30](https://www.adafruit.com/product/4867)[air quality sensor](https://www.adafruit.com/product/4867)] measuring the air's temperature, humidity, and CO2 level.   There is a photoresistor at the top of SnifferBuddy to indicate whether the grow lights are on or off. The brain behind SnifferBuddy is an ESP286 running [Tasmota firmware](https://tasmota.github.io/docs/About/). The Tasmota software publishes the readings over mqtt to an mqtt broker running on [Gus()](gus).
### Supported Sensors
SnifferBuddy's sensors were chosen for their accurate CO2 readings. Initially, Buddies use temperature and humidity readings. Eventually, we will also monitor and adjust CO2 levels, but first we need to optimize the grow area for proper water distribution in the air and soil.

The [SCD-30](https://www.adafruit.com/product/4867) and [SCD-40](https://www.adafruit.com/product/5187) sensors are currently supported. I initially used the SCD-30, but later switched to the SCD-40 because it is more affordable and smaller in size, yet still of high quality.


```{figure} images/snifferbuddy_in_growtent.jpg
:align: center
:height: 350

A Happy SnifferBuddy with an SCD-30 Sensor hanging about
```

```{figure} images/snifferbuddy_scd40_inaction.jpg
:align: center
:height: 350

A Happy SnifferBuddy with an SCD-40 Sensor hanging about
```


(make_snifferbuddy)=
## Let's Make One {material-regular}`build;1em;sd-text-success`
```{button-link} https://github.com/solarslurpi/GrowBuddies/discussions
:outline:
:color: success

 {octicon}`comment;1em;sd-text-success` Comments & Questions
```

```{note}
SnifferBuddy sends out MQTT messages containing sensor readings as the payload. It can be used in any MQTT environment. If you have set up Gus, it will be able to handle the messages sent by SnifferBuddy. This document assumes that you have already built Gus.
```
Once plugged in and working, you will be able to (compliments of [Gus](gus)):
- Store CO2, humidity, and temperature readings into an influxdb table (referred to as a measurement influxdb terminology) influxdb.
- Visualize your readings using grafana.
### Gather The Materials

- [SCD30 sensor or SCD40 sensor](https://www.adafruit.com/product/4867) component.
```{warning} The SCD40 driver is not included by default in the Tasmota sensor build for the ESP286.  I compiled a Tasmota sensor build that includes the SCD40.  There will also be different Tasmota installation steps.
```
- [ESP8286](https://www.aliexpress.us/item/2251832645039000.html) component.
- Photoresistor and 10K through hole resistor.  I had a lot of these kicking around. I bought something similar to [this kit](https://amzn.to/3yNZtZd).
- 3D printer and PLA filament for printing out [the enclosure](enclosure).
- Superglue for gluing the top Wemos part of the enclosure to the cap part of the enclosure.
- USB cord and plug the ESP8286 to power.
- 4 4mm M2.5 or M3 bolts.
(enclosure)=
### Make the Enclosure
Enclosures are made in Fusion 360 and printed on a Prusa MK3S printer.

#### SCD-30
```{button-link} https://github.com/solarslurpi/GrowBuddies/tree/main/enclosures/SnifferBuddy
:outline:
:color: success

 {octicon}`file-directory;1em;sd-text-success` Directory containing scd-30 enclosure files
```
To make the enclosure, download and print the 4 mesh files.
:::{figure} images/snifferbuddy_parts_on_printer_plate.jpg
:align: center
:height: 350

SnifferBuddy Enclosure Parts
:::

I use the F360 app extension [Parameter I/O](https://apps.autodesk.com/FUSION/en/Detail/Index?id=1801418194626000805&appLang=en&os=Win64) while modeling to import/export the parameters found in [SnifferBuddyParams.csv](https://github.com/solarslurpi/GrowBuddies/blob/c100124acaab285eadb284a5e7015e569ed76d3c/enclosures/SnifferBuddy/SnifferBuddyParams.csv).
#### SCD-40
```{note} Thank you, [sumpfing](https://www.thingiverse.com/sumpfing/designs), for your [modular Wemos D1 modular design]().
```
```{button-link} https://github.com/solarslurpi/GrowBuddies/tree/main/enclosures/SnifferBuddy/scd-40
:outline:
:color: success

 {octicon}`file-directory;1em;sd-text-success` Directory containing scd-40 enclosure files
```
The SCD-40 I built is made of two rings as shown in the image:

```{figure} images/snifferbuddy_scd40_enclosure.jpg
:align: center
:scale: 60

SCD-40 Ring Design
```
Moving forward, I will use a third ring for the photoresistor and put it between the bottom and scd-40 ring.



### Wire the Components Together
Wiring is the hardest part.
```{figure} images/snifferbuddy_scd40_wiring.jpg
:align: center
:scale: 60

SCD-40 Wired Up
```
```{div} sd-text-info
- Photoresistor
```
```{div} sd-text-success
- Wemos D1 ESP286
```
```{div} sd-text-danger
- SCD-40
```
```{note} The images show that the photoresistor was placed in the bottom ring near the USB port opening. However, this causes interference between the wires and the placement of the ESP286 in the bottom ring. In future builds, I will use a ring similar to the one used for the SCD-40 to eliminate this interference.
```

:::{figure} images/SnifferBuddy_wiring.jpg
:align: center
:scale: 100

SnifferBuddy SCD-40 Wiring
:::
I chose the ESP826 because I decided to use [Tasmota](https://tasmota.github.io/docs/) to send sensor readings via MQTT. Tasmota's original goal was to provide MQTT and OTA firmware for ESP8266-based ITEAD Sonokff devices, so I figured it made sense to use the same chip. I did encounter an issue with the Wemos D1 ESP286 when I made the first SnifferBuddy, but the ESP826 is generally very inexpensive and reliable. I ordered some from [Aliexpress](https://www.aliexpress.us/item/2251832645039000.html) and added a photoresistor to the top to determine if the grow lights were on or off. This helps me to know when to provide daytime or nighttime care for my plants.

I used a wired 4-pin JST SH connector to connect the Wemos D1 to the SCD sensor. Wiring can be challenging, so I summarized my thoughts on it [in a separate document](wiring_doc). By soldering the SDA, SCL, 5V+, and GND lines to the Wemos D1 pins, I was able to establish connectivity for the I2C lines of the SCD-40. In addition, I wired up the photoresistor. However, as noted, I should have used another ring for this.

A photoresistor circuit uses a voltage divider to measure the voltage.  This gives us the info we need to determine whether the LED lights are on.  Activities going on during the day - like adding humidity - is not something needed at night.

A pull-up or pull-down 10K (probably up to 100K) can be used.   I prefer using a pull-up resistor because I found that the wiring was easier to manage this way.


### Install Tasmota
Time to install Tasmota onto the ESP8286.  See [Tasmota Installation](tasmota_installation).

#### Verify Install
You can use a tool like [mqtt explorer](mqtt_explorer) to see if SnifferBuddy is sending out mqtt messages.

(snifferbuddy_storereadings)=
## Store Readings {material-outlined}`storage;1em;sd-text-success`
```{button-link} https://github.com/solarslurpi/GrowBuddies/discussions
:outline:
:color: success

 {octicon}`comment;1em;sd-text-success` Comments & Questions
```

The `store-readings` script highlights the capabilities of the interactions between SnifferBuddy and [Gus](gus).

The script:

- Returns SnifferBuddy readings **including** vpd.
- Stores SnifferBuddy readings into an influxdb table within the database.
- Keeps the code aware of SnifferBuddy's status.
- Shows [Gus](gus)'s logging capability.

```{attention}
Before running the `store-readings` script:
1. There must be a working SnifferBuddy and Gus.
2. The steps below must be completed.
```

```{button-link} https://github.com/solarslurpi/GrowBuddies/blob/930420abc7ddd4cf4c74c408d61819eec0968a44/growbuddies-project/growbuddies/examples/snifferbuddy_storereadings.py
:outline:
:color: success

 {octicon}`mark-github;1em;sd-text-success` View Code
```

### 1. Get into a Python Virtual Environment
A Python virtual environment with the growbuddies package installed must exist before running the Python script.  We'll run the script on Gus (the Raspberry Pi Server).
- Get to a command line prompt on Gus.
- Create a folder where the script will be run, e.g.:
```
$mkdir growbuddies
```
- Change into this directory, e.g.:
```
$cd growbuddies
```
- Make sure you have Python3 on Gus. e.g.:
```
$ python3 --version
Python 3.9.2
```
- Create a Python Virtual Environment using the venv Python module.  e.g.:
```
python3 -m venv .venv
```
- Activate the Virtual Environment.  e.g.:
```
$ source .venv/bin/activate
(.venv) pi@gus:~/test$

(.venv) pi@gus:~/test$ python --version
Python 3.9.2
```
The prompt is a visual clue we are now within the Virtual Environment.
### 2. Install the GrowBuddies package
```
(.venv) pi@gus:~/test$ pip install GrowBuddies --upgrade
```
```{note}
Including the `--upgrade` option will upgrade the GrowBuddies package to the latest version.  This will matter when running the script.
```
### 3. Run the Script
```
(.venv) pi@gus:~/test$ store-readings
```
You should start seeing a lot of logging lines.  These give you a great idea what is going on in the code.  If you are able to store readings into influxdb,
```{literalinclude} store-readings.txt
:language: bash
```

```{eval-rst}
.. automodule:: growbuddies.__main__
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
A plot of SnifferBuddyReadings for vpd
:::

The results point to an average vpd at that date/time range of about 1.3.
### Analyze Readings
Looking at [FLU's VPD Chart](https://www.canr.msu.edu/floriculture/uploads/files/Water%20VPD.pdf)
:::{figure} images/vpd_chart.jpg
:align: center
:scale: 75

FLU's VPD Chart
:::

```{danger}
A vpd reading of 1.3 is saying the grow environment is stressful for the plant.
```
The humidity or the temperature could be adjusted.  Here is a plot of the temperature and vpd.  While the vpd averages about 1.3, the temperature ranges between 73 and 75.  This is because my grow tent environment is in my house, which is climate controlled.  The LED lights raise the temperature a bit.  The fans cool the temperature a bit.  It's pretty ideal.  Thus, [MistBuddy](mistbuddy_doc) focuses on turning a humidifier on and off for just the right amount of time.

:::{figure} images/grafana_snifferbuddyreadings_vpd._and_temp.jpg
:align: center
:scale: 65

A plot of SnifferBuddyReadings for vpd and temperature.
:::


## Run as a Service
Running {ref}`snifferbuddy_storereadings` over ssh will stop when the desktop gets connected.  What needs to happen is to set up {ref}`snifferbuddy_storereadings` as a [Systemd service](systemd_doc).

