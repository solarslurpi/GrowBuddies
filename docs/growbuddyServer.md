# GrowBuddy Server
The GrowBuddy Server is a Raspberry Pi running:
- the Raspberry Pi OS with SSH for remote connecting.
- mqtt.
- influxdb.

## Materials
- Raspberry Pi 3 or 4.  At the time of this writing, there is a shortage of Raspberry Pis.  I have had the best luck from [Adafruit](https://www.adafruit.com/?q=raspberr&sort=BestMatch).
- Power Source for the Raspberry Pi. __Note: the Raspberry Pi 4 (5V via USB type-C up to 3A) uses a different power supply than the Raspberry Pi 3 (5V via micro USB up to2.5A)__
- [microSD card with full size adapter](https://amzn.to/3W3yvHa)
- [Enclosure](print_enclosure)
## Install Raspberry Pi OS
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
- Enter growbuddy for the hostname and enable SSH with password authentication.
- Fill in the other options - wifi, username/password, wifi, and local settings.

:::{figure} images/rasppi_lite_install_3.jpg
:align: center
:scale: 75

Setup Options
:::
- Click Save, the Write to install the Rasp Pi OS Lite OS with the options you entered.

- Remove the SD card from the reader.
- Insert the microSD into the Raspberry Pi.

### Verify the Install
Go to a terminal window on your Mac or PC and type:
```
ssh pi@growbuddy
```  
After entering your password, you should be in the command prompt:
```
pi@growbuddy:~ $
```
If you cannot reach the growbuddy raspberry pi, first check to see if the raspberry pi is on your home wifi by using a utility like [Angry IP](https://angryip.org/).  If it is not, perhaps [this troubleshooting guide](raspi-nowifi) helps.

(print_enclosure)=
## Print the Enclosure
I chose [Malolo's screw-less/snap fit Raspberry Pi 3 and 4 cases](https://www.thingiverse.com/thing:3723561).  Specifically the one color slot base and the two color hex top.  You can choose what you want.  I have included the stl files I used within [this folder](https://github.com/solarslurpi/GrowBuddy/tree/12164fa3791e3b8eb33d5ebfc06c2096fe7cf1e7/enclosures/GrowBuddy).

## Install mqtt
mqtt is how the Buddies text message each other. For example, [SnifferBuddy](snifferbuddy.md) sends out (i.e.: publishes in mqtt terminology) over wifi an mqtt message like this:
```
{"Time":"2022-09-06T08:52:59",
  "ANALOG":{"A0":542},
  "SCD30":{"CarbonDioxide":814,"eCO2":787,"Temperature":71.8,"Humidity":61.6,"DewPoint":57.9},"TempUnit":"F"}
}
```
[vpdBuddy](vpdBuddy.md) is listening (i.e.: subscribed to) for messages from SnifferBuddy 
We use the mosquitto broker running on a raspberry pi.
### Resources
- [Installing mosquitto on Rasp Pi](https://pimylifeup.com/raspberry-pi-mosquitto-mqtt-server/)
- [mqtt Explorer](http://mqtt-explorer.com/) - this tool does exactly what the name implies.  It allows you to explore the mqtt traffic as it whizzes by.  You can also publish messages.  Very handy.
- [YouTube video on mqtt Last Will and Testament](https://www.youtube.com/watch?v=dNy9GEXngoE).  Good to know how this works (and why).
- [Clearing mqtt retained messages](https://community.openhab.org/t/clearing-mqtt-retained-messages/58221).  Another good to know.
- [How Tasmota handles mqtt Last Will and Testament](https://tasmota.github.io/docs/MQTT/#lwt-topic-last-will-and-testament)
### Configure and Install
- Create the connect.conf file. From a terminal open on the Raspberry Pi:
  - `$ cd /etc/mosquitto/confd.`
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
- Install Mosquitto [following PiMyLife's steps](https://pimylifeup.com/raspberry-pi-mosquitto-mqtt-server/)
### Play
Open up [MQTT explorer](http://mqtt-explorer.com/) and connect to GrowBuddy.
:::{figure} images/mqtt_explorer_before_snifferbuddy.jpg
:align: center
:scale: 80

GrowBuddy[1] mqtt broker
:::
_Note: The name of this server is GrowBuddy1 because GrowBuddy is being used._  Since there are no Buddies, the only traffic is the default traffic of the broker.
### Determining the Health of a Device
You may not need to know anything about this.  I have it here so I don't forget why this is in the code!

[MQTT's Last will and Testament - LWT](https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/) is an extremely useful feature to use for mqtt error debugging.  The Buddies sending mqtt messages are all Tasmota devices. [Refer to Tasmota's page](https://tasmota.github.io/docs/MQTT/#lwt-topic-last-will-and-testament) for advice on how LWT is implemented.

For example,  let's say we have a snifferbuddy up and running.
```
pi@growbuddy:~ $ mosquitto_sub -t "tele/snifferbuddy/LWT"
Online
Offline
Online
```
subscribing to the above topic shows initially SnifferBuddy is online.  I unplug.  Wait the 30 seconds that Tasmota by default sets the keep alive time to.  An offline message is sent by the broker.  I then plug SnifferBuddy back in. Right after SnifferBuddy boots, we receive an Online message.

The [MQTT Esentials Page 9](https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/) article lists several states that cause the broker to publish the LWT message.

issuing the `status 6` command on the Tasmota command line informs us on the mqtt settings for this Tasmota device:
```
 MQT: stat/snifferbuddy/STATUS6 = {"StatusMQT":{"MqttHost":"growbuddy","MqttPort":1883,"MqttClientMask":"DVES_%06X","MqttClient":"DVES_25EEA5","MqttUser":"DVES_USER","MqttCount":1,"MAX_PACKET_SIZE":1200,"KEEPALIVE":30,"SOCKET_TIMEOUT":4}}
 ```
The mqtt info lets us know the mqtt keep alive time is 30 seconds.

## Troubleshooting

(raspi-nowifi)=
### Installed Raspberry Pi But Cannot SSH
You've verified the growbuddy Rasp Pi has an IP address.  However, perhaps you accidentally entered the wrong SSID or password for your wifi.  Or you forget to enable SSH.  You can manually configure these options.  
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



## Using Rsync 
Rsync is a very useful utiity on the Raspberry Pi.  I document my use here because I keep forgetting
how to use it.  Currently I am on a Windows PC.  The challenge is to start an Bash session in the right directory.
- open Explorer, go to the directory to use rsync, type in bash in the text field for the filepath.

:::{figure} images/explorer_with_bash.jpg
:align: center
:scale: 100

Getting to Bash Command Line Through Explorer
:::


A wsl window will open at this location.
```
sudo rsync -avh pi@growbuddy:/home/pi/growbuddy_1_data.zip  .

```