# Getting Started
Let's start with the core components:
- the Raspberry Pi running the backend services including the mqtt broker.
- [SnifferBuddy](snifferbuddy_page)

Once these are up and running, we can add the components of [VPD Buddy](vpdbuddy) and Soil Moisture Buddy.

## Install the GrowBuddy Server.
### Materials
- Raspberry Pi 3 or 4.  At the time of this writing, there is a shortage of Raspberry Pis.  I have had the best luck from [Adafruit](https://www.adafruit.com/?q=raspberr&sort=BestMatch).
- Power Source for the Raspberry Pi. __Note: the Raspberry Pi 4 (5V via USB type-C up to 3A) uses a different power supply than the Raspberry Pi 3 (5V via micro USB up to2.5A)__
- [microSD card with full size adapter](https://amzn.to/3W3yvHa)
### Install Raspberry Pi OS
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

#### Verify the Install
Go to a terminal window on your Mac or PC and type:
```
ssh pi@growbuddy
```  
After entering your password, you should be in the command prompt:
```
pi@growbuddy:~ $
```
If you cannot reach the growbuddy raspberry pi, first check to see if the raspberry pi is on your home wifi by using a utility like [Angry IP](https://angryip.org/).  If it is not, perhaps [this troubleshooting guide](raspi-nowifi) helps.

### Print Enclosure
The Raspberry Pi enclosure

### Install the mqtt Broker
The Buddies communicate over a home's wifi using mqtt
### Troubleshooting

(raspi-nowifi)=
## Installed Raspberry Pi But Cannot SSH
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





99999999999999999999999999
- Install and configure an mqtt broker.

- Install and configure influxdb.

Step 2: Create a folder on the Raspberry Pi that will hold the GrowBuddy Python classes.
========================================================================================
Make a directory, something like:

::
    $mkdir GrowBuddy

Step 3: Create a Python virtual environment.
============================================
`Bernard's video around 21 minutes ingives a great explanation of virtual environments if these are unfamiliar to you <https://youtu.be/ApDThpsr2Fw?t=1274>`_ .  Given Bernard's recommendation,
we'll use `virtualenv <https://virtualenv.pypa.io/en/latest/>`_ 

test

adfljaldfkjdklajf
adflajsdflkadjsfkj