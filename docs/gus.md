
# Gus
```{figure} images/Gus_2.jpg
:align: center
:scale: 30

A Rasp Pi 3 Gus and a Rasp Pi 4 Gus
```
## About
 Gus:

 - runs on a Raspberry Pi.
 - includes an enclosure that needs to be 3D printed.
 - uses the local wi-fi.
 - is an MQTT Broker that can respond to GrowBuddies' MQTT messages.
 - can store SnifferBuddy readings in an influx db database.
 - can plot the SnifferBuddy readings in Grafana.
 - can manage an "ideal" vpd setpoint.
 - can manage a CO2 level setpoint.

```{note} Gus presumes a [SnifferBuddy](snifferbuddy) is currently active on the same WiFi.

```{button-ref} make_snifferbuddy
:ref-type: myst
:align: center
:color: success
:shadow:
Make SnifferBuddy
```

(make_gus)=
## Make Gus

To ensure that Gus is able to handle the demands of his tasks, he is equipped with a robust set of tools. The process of setting up Gus begins with constructing his hardware, followed by installing the operating system and necessary tools to bring him to life.

### 1. Get the parts together

Below are the parts assuming the Raspberry Pi 4 with 4 GB is used.
The hardware needed to build Gus includes:

| Component | Cost | Reason |
|-----------|------|--------|
| [Rasp 4 w 4GB](https://www.adafruit.com/product/4296) | $55.00 | This is what I use.  It is working well.
| [USB-C Power Supply for Rasp Pi](https://www.adafruit.com/product/4298) | $7.95 | Official Raspberry Pi Power Supply 5.1V 3A with USB C one with data wires. __Note: the Raspberry Pi 4 (5V via USB type-C up to 3A) uses a different power supply than the Raspberry Pi 3 (5V via micro USB up to 2.5A)__
| [micro SD card](https://amzn.to/3W3yvHa) | $16 | Two amazon basics 64 GB.
| enclosure | pennies | The model I chose is [Malolo's](https://www.thingiverse.com/thing:3723561) [screw-less](https://www.thingiverse.com/thing:3723561) snap-fit[ Raspberry Pi](https://www.thingiverse.com/thing:3723561) 3 and 4 cases. <br>Specifically the one-color slot base and the two-color hex top.

### 2. Print out the Enclosure
#### Raspberry Pi 4 Case
Raspberry Pi 4 (Recommended.  It is the green Gus in the above image):
| Component | File
|-----------|------|
| top | The top can be multicolored yet does not require a 3D printer that can print multiple filaments at once.<br>The two files include [Pi4 Top Hex color 1](../enclosures/GrowBuddy/Pi4_Top_Hex_MM2_Color1.stl) and [Pi4 Top Hex color 2](../enclosures/GrowBuddy/Pi4_Top_Hex_MM2_Color2.stl).  If you are unsure how to print for <br>multi-color, Malalo has provide [multi-color printing directions](https://www.thingiverse.com/thing:3719217)
| bottom | [Pi4 Bottom with slots](../enclosures/GrowBuddy/Pi4_Bottom_Slots_SM.stl)
#### Raspberry Pi 3 Case
Raspberry Pi 3 (I've tried it.  But better just to start with the Raspberry Pi 4):
| Component | File |
|-----------|------|
| top | Similar to the top for the Raspberry Pi 4, two files are used.  The first is [Pi3 Top Hex color 1](../enclosures/GrowBuddy/Pi3_Top_Hex_MM2_Color1.stl).<br>The second is [Pi3 Top Hex color 2](../enclosures/GrowBuddy/Pi3_Top_Hex_MM2_Color2.stl)
| bottom | [Pi3 Bottom with slots](../enclosures/GrowBuddy/PI3_Bottom_Slots_SM.stl)

Fit the Raspberry Pi into the enclosure after it has been printed.
#### Put the Pi in its Enclosure
I found it pretty simple to put the pi into the enclosure once it had been printed.
(_install_pi)=
### 3. Install The Raspberry Pi OS
- Download [the Raspberry Pi Installer](https://www.raspberrypi.com/software/).
- Click to choose OS.  Only Raspberry Pi Lite is needed.  Choose this option:

:::{figure} images/rasppi_lite_install.jpg
:align: center
:scale: 75

Rasp Pi Lite OS
:::
- Choose the SD card, then go into Settings by clicking on the cog.

:::{figure} images/rasppi_lite_install_2.jpg
:align: center
:scale: 75

Choose the cog
:::
- Enter `gus` for the hostname and enable SSH with password authentication.
- Fill in the other options - wifi, username/password, wifi, and local settings.

:::{figure} images/rasppi_lite_install_3.jpg
:align: center
:scale: 75

Setup Options
:::
- Click Save to install the Rasp Pi OS Lite OS with the options you entered.

- Remove the SD card from the reader.
- Insert the microSD into the Raspberry Pi.

### 4. Verify the Install
After the Raspberry Pi, has booted up, go to a terminal window on your Mac or PC and type:
```
ssh pi@gus
```
After entering your password, you should be in the command prompt:
```
pi@gus:~ $
```
If you cannot reach Gus from your Mac/PC, first check to see if the raspberry pi is on your home wifi by using a utility like [Angry IP](https://angryip.org/).  If it is not, perhaps [this troubleshooting guide](raspi-nowifi) helps.

### 5. Install mqtt
The buddies use mqtt to send and receive payloads and commands. Gus runs the [Mosquitto Broker](http://www.steves-internet-guide.com/mosquitto-broker/).  Mosquitto is a lightweight open source message broker.  It works well.
#### Configure the Mosquitto MQQT Broker

Before installing the service, some unique settings are needed in Mosquitto's config file.

- Create the connect.conf file. From a terminal open on the Raspberry Pi:
  - `$ cd /etc/mosquitto/conf.d`
  - `$ sudo nano connect.conf`
  - copy/ paste the following into the new connect.conf file:
```
listener 1883
protocol mqtt

listener 9000
protocol websockets

allow_anonymous true
```
  - save and exit.
#### Install the Mosquitto MQQT Broker
- Install Mosquitto [following PiMyLife's steps](https://pimylifeup.com/raspberry-pi-mosquitto-mqtt-server/)
(mqtt_explorer)=
#### Observe Messages
Open up [MQTT explorer](http://mqtt-explorer.com/) and connect to gus.
:::{figure} images/mqtt_explorer.jpg
:align: center
:scale: 60

Gus mqtt broker
:::
The image points out there is a SnifferBuddy sending mqtt messages to Gus.

### 6. Install influxdb
[InfluxDB (v1.8)](https://www.influxdata.com/) is a time series-based database service that is free to use on the Raspberry Pi.

Follow [PiMyLifeUp's directions](https://pimylifeup.com/raspberry-pi-influxdb/) to install.

### 7. Install Grafana
I followed [the steps to install grafana](https://grafana.com/tutorials/install-grafana-on-raspberry-pi/).
:::{warning}
 When I tried:
```
sudo apt-get update
```
I got the message:
```
E: Conflicting values set for option Signed-By regarding source https://packages.grafana.com/oss/deb/ stable: /usr/share/keyrings/grafana-archive-keyrings.gpg !=
E: The list of sources could not be read.
```
after bumbling about on Google/StackOverflow, I ended up:
```
$ sudo nano /etc/apt/sources.list.d/grafana.list
```
and deleted the duplicate lines. Then `sudo apt-get update` worked.
:::
