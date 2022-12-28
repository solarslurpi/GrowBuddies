
# Gus
:::{div}
<img src="images/hamster.jpg" class="sd-avatar-md sd-border-3">
:::



## About {material-regular}`question_mark;1em;sd-text-success`
Gus, a Raspberry Pi 3 or 4 running Bullseye OS, is able to store and visualize not only SnifferBuddy readings, but also vpd values.

:::{div}
<img src="https://docs.google.com/drawings/d/e/2PACX-1vTjks0iZHIZyD4VEdOo01_se0jn_CgJu9JUCee-rUhXBmFfykmObBkpqSUFBkOvnIdisiIzygPvDeZa/pub?w=984&amp;h=474&amp;align=middle">
:::

 As you can see, Gus has a lot of tools to help GrowBuddies.  These include [a mosquitto mqtt broker](http://www.steves-internet-guide.com/mqtt-works/) that holds the latest SnifferBuddy mqtt message.  If instructed to do so, Gus can store the SnifferBuddy readings in an influxdb database.  If the readings are stored, you no longer need Gus to access the readings.  For example, you can create simple to sophisticated dashboards using Grafana.  Or look at the data through apps that speak to influxdb's API.

Gus is equipped with a range of tools to assist GrowBuddies, including [a mosquitto mqtt broker](http://www.steves-internet-guide.com/mqtt-works/), which holds the latest SnifferBuddy mqtt message. Additionally, Gus can store SnifferBuddy readings in an influxdb database upon request. This allows for the creation of dashboards using Grafana or access to the data through apps that utilize influxdb's API, eliminating the need for ongoing access to Gus for reading purposes.

(make_gus)=
## Let's Make One {material-regular}`build;1em;sd-text-success`
```{button-link} https://github.com/solarslurpi/GrowBuddies/discussions
:outline:
:color: success

 {octicon}`comment;1em;sd-text-success` Comments & Questions
```

To ensure that Gus is able to handle the demands of his tasks, he is equipped with a robust set of tools. The process of setting up Gus begins with constructing his hardware, followed by installing the operating system and necessary tools to bring him to life.

Here are two I've made:
```{image} images/Gus_2.jpg
:align: center
:scale: 40
```
The hardware for the green device (on the left) consists of components from the Raspberry Pi 4, while the purple device is built with components from the Raspberry Pi 3B+.
### Rasp Pi + Enclosure
#### Gather The Materials
First, you'll need to gather the materials.

- A Raspberry Pi 3B+ or 4.  At the time of this writing, there is a shortage of Raspberry Pis.  I have had the best luck with [Adafruit](https://www.adafruit.com/?q=raspberr&sort=BestMatch).
- A Power Source for the Raspberry Pi. __Note: the Raspberry Pi 4 (5V via USB type-C up to 3A) uses a different power supply than the Raspberry Pi 3 (5V via micro USB up to 2.5A)__.
- A [microSD [card with ](https://amzn.to/3W3yvHa)full-size[ adapter](https://amzn.to/3W3yvHa).
- An Enclosure needs to be printed out on a 3D printer.  The model I chose is [Malolo's [screw-less/](https://www.thingiverse.com/thing:3723561)snap-fit[ Raspberry Pi](https://www.thingiverse.com/thing:3723561) 3 and 4 cases](https://www.thingiverse.com/thing:3723561).  Specifically the one-color slot base and the two-color hex top.  You can choose what you want.  I have included the stl files I used.
#### Put the Pi in its Enclosure
I found it pretty simple to put the pi into the enclosure once it had been printed.

### Install The Software
#### Resources
I found the following stuff on the web to be helpful:
- [How to embed degree symbols (like &#8457;)](https://www.alt-codes.net/degree_sign_alt_code.php).s
- [Python Virtual Environments](https://www.youtube.com/watch?v=ApDThpsr2Fw&t=1295s) at this point in the video, the difference between `virtualenv` and `venv` is explained.  More details are given in [Virtualenv RTD](https://virtualenv.pypa.io/en/latest/).
- [Installing mosquitto on Rasp Pi](https://pimylifeup.com/raspberry-pi-mosquitto-mqtt-server/)
- [mqtt Explorer](http://mqtt-explorer.com/) - this tool does exactly what the name implies.  It allows you to explore the mqtt traffic as it whizzes by.  You can also publish messages.  Very handy.
- [YouTube video on mqtt Last Will and Testament](https://www.youtube.com/watch?v=dNy9GEXngoE).  Good to know how this works (and why).
- [Clearing mqtt retained messages](https://community.openhab.org/t/clearing-mqtt-retained-messages/58221).  Another good to know.
(tasmota_lwt)=
- [How Tasmota handles mqtt Last Will and Testament](https://tasmota.github.io/docs/MQTT/#lwt-topic-last-will-and-testament)
(raspPi_install)=
#### Install The Raspberry Pi OS
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

##### Verify the Install
Go to a terminal window on your Mac or PC and type:
```
ssh pi@gus
```
After entering your password, you should be in the command prompt:
```
pi@gus:~ $
```
If you cannot reach Gus from your Mac/PC, first check to see if the raspberry pi is on your home wifi by using a utility like [Angry IP](https://angryip.org/).  If it is not, perhaps [this troubleshooting guide](raspi-nowifi) helps.


(mqtt_install)=
#### Install mqtt
The buddies use mqtt to send and receive payloads and commands. For example, [SnifferBuddy](snifferbuddy.md) sends out (i.e.: publishes in mqtt terminology) over wifi an mqtt message like this:
```
{"Time":"2022-09-06T08:52:59",
  "ANALOG":{"A0":542},
  "SCD30":{"CarbonDioxide":814,"eCO2":787,"Temperature":71.8,"Humidity":61.6,"DewPoint":57.9},"TempUnit":"F"}
}
```
Gus runs the [Mosquitto Broker](http://www.steves-internet-guide.com/mosquitto-broker/).  Mosquitto is a lightweight open source message broker.  It works well.  Thank you to the open-source community.
##### Configure the Mosquitto MQQT Broker

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
##### Install the Mosquitto MQQT Broker
- Install Mosquitto [following PiMyLife's steps](https://pimylifeup.com/raspberry-pi-mosquitto-mqtt-server/)
(mqtt_explorer)=
##### Observe Messages
Open up [MQTT explorer](http://mqtt-explorer.com/) and connect to gus.
:::{figure} images/mqtt_explorer.jpg
:align: center
:scale: 60

Gus mqtt broker
:::
The image points out there is a SnifferBuddy sending mqtt messages to Gus.
(mqtt_LWT)=
##### Using MQTT To Determine Device Health
You may not need to know anything about this.  I have it here so I don't forget why this is in the code!

[MQTT's Last will and Testament - LWT](https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/) is an extremely useful feature to use for mqtt error debugging.  The Buddies sending mqtt messages are all Tasmota devices. [Refer to Tasmota's page](https://tasmota.github.io/docs/MQTT/#lwt-topic-last-will-and-testament) for advice on how LWT is implemented.

For example,  let's say we have a SnifferBuddy up and running.
```
pi@gus:~ $ mosquitto_sub -t "tele/snifferbuddy/LWT"
Online
Offline
Online
```
subscribing to the above topic shows initially SnifferBuddy is online.  I unplug.  Wait the 30 seconds that Tasmota by default sets the keep-alive time to.  An offline message is sent by the broker.  I then plug SnifferBuddy back in. Right after SnifferBuddy boots, we receive an Online message.

The [MQTT Esentials Page 9](https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/) article lists several states that cause the broker to publish the LWT message.

issuing the `status 6` command on the Tasmota command line informs us of the mqtt settings for this Tasmota device:
```
 MQT: stat/snifferbuddy/STATUS6 = {"StatusMQT":{"MqttHost":"gus","MqttPort":1883,"MqttClientMask":"DVES_%06X","MqttClient":"DVES_25EEA5","MqttUser":"DVES_USER","MqttCount":1,"MAX_PACKET_SIZE":1200,"KEEPALIVE":30,"SOCKET_TIMEOUT":4}}
 ```
The mqtt info lets us know the mqtt keep alive time is 30 seconds.
(influxdb_install)=
#### Install influxdb
[InfluxDB (v1.8)](https://www.influxdata.com/) is a time series-based database that is free to use on the Raspberry Pi.  There can be multiple databases.

```{admonition} Gus as the database name
I stick with the database name of Gus.  If you look in growbuddies_settings.json, you will see influxdb setting for the database.
```
TODO: command line utility
$influx
show databases

sudo apt install influxdb-client
Follow [PiMyLifeUp's directions](https://pimylifeup.com/raspberry-pi-influxdb/) to install.

#### Install Grafana
I followed [the steps to install grafana](https://grafana.com/tutorials/install-grafana-on-raspberry-pi/). When I try:
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
## Playtime {material-regular}`celebration;1em;sd-text-success`
```{note} You must build [SnifferBuddy](snifferbuddy) and [Gus](gus) before playtime can begin.
```
If you have a SnifferBuddy that is sending out MQTT messages and a Gus device that is running an MQTT broker and InfluxDB database,
you can access the command line of the Gus device and type the following command:
```bash
store-readings
```
This will start running the `__main__.py` script.
```{button-link} https://github.com/solarslurpi/GrowBuddies/blob/main/growbuddiesproject/growbuddies/__main__.py
:outline:
:color: success

 {octicon}`file-code;1em;sd-text-success` View Source
```
The following text describes the code found in the `__main.py__` file.

```{eval-rst}
.. automodule:: growbuddies.__main__
   :members:

.. autoclass:: Callbacks
   :members:
```


## Useful Raspberry Pi Stuff

(raspi-nowifi)=
### Installed Raspberry Pi But Cannot SSH
You've verified Gus has an IP address.  However, perhaps you accidentally entered the wrong SSID or password for your wifi.  Or you forget to enable SSH.  You can manually configure these options.
- Add "SSH" file to the root of the image.  We do this by opening a terminal on the boot partition and typing `$touch ssh`
- Create the `wpa_supplicant.conf` file : `$touch wpa_supplicant.conf`.  Copy the contents into the file `nano wpa_supplicant.conf`:
```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOURSSID"
    psk="YOURPWD"
}

```
_Note: Multiple wifi networks can be set up by following [this example](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md)_:

```
network={
    ssid="SchoolNetworkSSID"
    psk="passwordSchool"
    id_str="school"
}

network={
    ssid="HomeNetworkSSID"
    psk="passwordHome"
    id_str="home"
}
```

Changing the ssid and psk to match your network.
- Remove the SD-card.
- Put the SD-card into the Rasp-Pi's micro-SD port.
- Power up the Rasp Pi.  Hopefully wireless is working!


### Using Rsync
Rsync is a very useful utility on the Raspberry Pi.  I document my use here because I keep forgetting
how to use it.  Currently, I am on a Windows PC.  The challenge is to start a Bash session in the right directory.
- open Explorer, go to the directory to use rsync, and type in bash in the text field for the file path.

:::{figure} images/explorer_with_bash.jpg
:align: center
:scale: 100

Getting to Bash Command Line Through Explorer
:::

A wsl window will open at this location.
```
sudo rsync -avh pi@gus:/home/pi/mydata.zip  .

```
### Change Text
From within a directory within multiple files:
```
find /path -type f -exec sed -i 's/oldstr/newstr/g' {} \;
```
### OSError: [Errno 98] Address already in use

#### Find the ProcessID

Using the command:
```
 pi@gus:~/gus $
pi        2465  0.2  0.4  25956 17520 pts/0    T    09:31   0:00 /home/pi/gus/py_env/bin/python /home/pi/gus/py_env/bin/sphinx-autobuild docs docs/_build/html
pi        2641  0.0  0.0   7344   508 pts/0    S+   09:34   0:00 grep --color=auto sphinx-autobuild
```
The PID we are interested in is 2465.
#### Kill the Process
Onto the kill command, which needs sudo privileges.
```
pi@gus:~/gus $ sudo kill -9 2465
[1]+  Killed                  sphinx-autobuild docs docs/_build/html  (wd: ~/gus/docs)
(wd now: ~/gus)
```
### Check which Python is in Use
It's best practice to run Python code in a virtual environment.  To check to see which interpreter is running:
```
py_env) pi@gus:~/growbuddies $ python
Python 3.7.3 (default, Jan 22 2021, 20:04:44)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> sys.executable
'/home/pi/growbuddies/py_env/bin/python'
```
### Check Rasp Pi OS Version stuff
```
(py_env) pi@gus:~/growbuddies/growbuddies-project $ uname -a
Linux gus 5.10.103-v7l+ #1529 SMP Tue Mar 8 12:24:00 GMT 2022 armv7l GNU/Linux

(py_env) pi@gus:~/growbuddies/growbuddies-project $ cat /etc/debian_version
10.13

(py_env) pi@gus:~/growbuddies/growbuddies-project $ cat /etc/rpi-issue
Raspberry Pi reference 2021-12-02
```
```{note} Debian 10 is Buster.  Debian 11 is Bullseye.
```
### Ignore a Page
If you don't want to include a document in the toctree, add :orphan: to the top of your document to get rid of the warning.

This is a File-wide metadata option. Read more from the [Sphinx documentation](https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html#file-wide-metadata).

### Packaging
There is so much history with Python.  Resource: [Python packaging](https://realpython.com/pypi-publish-python-package).