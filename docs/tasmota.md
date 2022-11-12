
# Tasmota


(before_installation)=
## Before You Begin Installation
Before you begin installation, check to see if the sensor you are using is included in the binary.  There is not much space on an ESP286 so it is especially relevant for this chip.  To check, go to [Tasmota's BUILDS documentation](https://tasmota.github.io/docs/BUILDS/).  Here we have a table listing which sensors are included.  The column to look at is labeled t.  The cells in this column let us know if the sensor build contains either, both, or none of the (ESP286/ESP32) drivers for the sensor.  An x means the sensor code is include.   For example, search for SCD40. The t entry has -/x.  This is saying __the SCD40 sensor code is not in the ESP286 build but is in the ESP32 build__.  If you want to add support for a sensor, follow the steps outlined in the [Compiling using GitPod](github_compile).

(tasmota_installation)=
## Install Tasmota

The easiest way requires you have the same ESP286 [the Wemos D1](https://www.aliexpress.us/item/2251832645039000.html) and **if you are building SnifferBuddy**, the [SCD30 sensor from Adafruit](https://www.adafruit.com/product/4867).  I have backed up my configuration which you restore onto your WemosD1 when you are installing Tasmota.

_Note: There is also a config file for a **[Tasmotized Sonoff plug](flash_tasmota)**_.
### Web Install
Install Tasmota using either the Edge or Chrome browser (web install doesn't work using the Brave browser).  Go to [Tasmota Install URL](https://tasmota.github.io/install/).
_Note:  If the USB/COM port can't be identified, the first thing to do is to check the cable.  The USB cable might not support data i/o.  If that doesn't work, check the USB driver.  The ESP286 or ESP32 may be using a driver that isn't installed on your Windows PC or Mac._

There are many Tasmota binaries that could be installed.  We want to install the Tasmota Sensors binary for the ESP286.
:::{figure} images/install_tasmota.jpg
:align: center
:scale: 100

Tasmota Web Install
:::
#### Connect to WiFi
The install includes connecting to the home wifi.

If you want to be sure the ESP286 has been "Tasmotized" correctly, you can use a tool like [Angry IP](https://angryip.org/) to show the IP address.
:::{figure} images/angry_ip_tasmota.jpg
:align: center
:scale: 70

Angry IP Scan Shows Tasmota
:::

Choose your adventure for the rest of install:
- [Restore Configuration](restore_config) if:
  - you are building a SnifferBuddy with [the Wemos D1](https://www.aliexpress.us/item/2251832645039000.html) and the [SCD30 sensor from Adafruit](https://www.adafruit.com/product/4867).
  - you are building a [Tasmotized Plug](flash_tasmota).
- [Install Without a Configuration File](install_without_config) if you do not want to use the configuration file or a configuration file does not exist for your hardware configuration.

(restore_config)=
#### Restore Config File

Choose **Restore Configuration**

:::{figure} images/tasmota_restore.jpg
:align: center
:scale: 60

Restore Configuration UI
:::
Tasmota config files have the .dmp extension.  The backup config file is:
- `/bin/Config_snifferbuddy_11.1.0.1.dmp` for SnifferBuddy.
- `/bin/Config_mistBuddy_fan_10.1.0.dmp` for the Tasmotized plug designated for mistBuddy's fan.
- `/bin/Config_mistBuddy_mister_10.1.0.dmp` for the Tasmotized plug designated for mistBuddy's mister Power Supply.

Choose the file for the component you are building and start the restore.


(install_without_config)=
### Install Without Config File
Now Visit the Device.  Go into Configure Module and choose:
- if you are building a sensor like SnifferBuddy, choose Generic(18) and then Save.
- if you are building a Tasmotized Sonoff plug, choose
#### Configure Host Name
I like to configure the Host Name as soon as possible so I can get to the device with a name.

:::{figure} images/tasmota_wifi_snifferbuddy.jpg
:align: center
:scale: 70

SnifferBuddy Host Name
:::

Here I chose the name SnifferBuddy-SCD40 to note this is a SnifferBuddy using the SCD40 sensor.  Click on Save.  Wait for the Main Menu to come back.
#### Configure GPIO pins
Go back into Configure, choose Configure Module.  From here set up the GPIO pins as shown in the image below.

:::{figure} images/tasmota_config_gpio_pins.jpg
:align: center
:scale: 70

Tasmota Setting GPIO pins
:::
(configure_mqtt)=
#### Configure mqtt
Go to Configure MQTT.
- Set the Host to growBuddy (assuming the mqtt broker is named growBuddy).
- Set the topic to the Buddy being enabled (in this case SnifferBuddy).
- Change the prefix part of the Full Topic to start with growBuddy.

:::{figure} images/tasmota_mqtt_config.jpg
:align: center
:scale: 70

Tasmota mqtt Settings
:::
Save and go back to the main menu.

#### Check mqtt
Using a tool like [MQTT Explorer](http://mqtt-explorer.com/)
:::{figure} images/tasmota_mqtt_explorer.jpg
:align: center
:scale: 70

MQTT Explorer
:::
We see in the image that the sensor reading for the photoresistor (A0) is available.  The value is 585.  The SCD40 values are not there.  This is because as noted in the section [Before You Begin Installation](before_installation), the SCD40 is not a part of the ESP286 sensors build.  The driver needs to be added separately as discussed above.
#### Commands
Tasmota support A LOT of [commands](https://tasmota.github.io/docs/Commands/).  The ones listed below were used on Tasmotized Buddies (like snifferBuddy).  Commands are accessed through clicking on the Console button in the main menu.
:::{figure} images/tasmota_main_screen.jpg
:align: center
:scale: 35

Tasmota main menu
:::
The main menu is then replaced with the console where commands can be entered.
:::{figure} images/tasmota_console.jpg
:align: center
:scale: 35

Tasmota main menu
:::

(set_time_between_readings)=
#### Set Time Between Readings
Set up the period between sending the sensor readings over mqtt using the `teleperiod` command.  e.g.:
```
teleperiod 60
```
sets sending readings via mqtt to occur every minute.
(set_date_time)=
#### set Local Time
This command set the correct timezone stuff for PST:

Use the web console to configure the Timezone (this shows Pacific time):
```
Backlog Timezone 99 ; TimeDST 0,2,03,1,3,-420 ; TimeSTD 0,1,11,1,2,-480
```
The 99 says to use TimeDST and TimeSTD. Use "time" to check.

[Thank you Craig's Tasmota page](https://xse.com/leres/tasmota/)

Or Keep It Simple and just change the timezone with the command `timezone -8` (see [Tasmota commands](https://tasmota.github.io/docs/Commands/#management)
#### Set Temperature Readings to F or C
Typing in the command without an option returns the current setting.
```
21:45:11.776 CMD: setoption8
21:45:11.782 MQT: growBuddy/snifferbuddy/RESULT = {"SetOption8":"ON"}
```
Weirdly, "ON" means temperature readings will be in Fahrenheit.
```
21:46:30.756 CMD: so8 0
21:46:30.761 MQT: growBuddy/snifferbuddy/RESULT = {"SetOption8":"OFF"}
```
The temperature is set to celsius with the command `so8 0`.  To Fahrenheit with the command `so8 1`.

#### Accomodate SCD30 Slow To Discover
The first time I used the SCD30 with Tasmota on a Wemos D1, it didn't work.  The reason is [discussed below](wemos_challenges).  `SetOption46` was added in Tasmota 12.1.1.  `SetOption46 0..255` stalls I2C component discovery for 0..255 * 10 milliseconds to let stabilize the local Wemos power. You might want to experiment with values like SO46 10 os SO46 20 for a 100mSec or 200mSec delay.

## Commands To Verify the Install
Two commands, `i2cscan` and `i2cdevice` are extremely helpful in determining if the software and wiring are correct.

### i2cscan
`i2cscan` is an extremely useful command.  Executing `i2cscan` from the console is useful to **show you if the i2c sensor is wired correctly**.  It is useful right after an install to see if the wiring to the ESP286 is correct.
```
21:41:54.158 CMD: i2cscan
21:41:54.179 MQT: growBuddy/snifferbuddy/RESULT = {"I2CScan":"Device(s) found at 0x62"}
```
The above is a verification that the wiring works for the ESP286/SCD40 I built since 0x62 is the SCD40's I2C address.

### i2cdriver
`i2cdriver` shows **the list of drivers that were loaded by the Tasmota build**.  For example, by default, the SCD40 is not in the ESP286 Tasmota Sensors build.  This is shown in [Tasmota's build table](https://tasmota.github.io/docs/BUILDS/).
```{image} images/scd_in_builds.jpg
:align: center
:scale: 70
```
I find the builds table challenging to read.  Here's my take:
- The rows are for each sensor where there is a Tasmota driver.
- The s column is for sensors.  I'm guessing (this is not obvious to me) the X (Sensor included) and - (Sensor not in build) in this column is referencing the **ESP286** Tasmota sensors build.
- The t column is for ESP286/ESP386 Tasmota build.  This column says the SCD30 and SCD40 are in the ESP32 Tasmota build - so I assume also in the ESP32 Sensor build since it is a subset.


```
21:40:49.852 CMD: i2cdriver
21:40:49.861 MQT: growBuddy/snifferbuddy/RESULT = {"I2CDriver":"7,8,9,10,11,12,13,14,15,17,18,20,24,29,31,36,41,42,44,46,48,62"}
```
From the results of i2cdriver, I can see the SCD40 (which sits on i2c address 0x62) is in this build.  I created a [custom build](github_compile) in order to include the SCD40 in the set of software drivers shown by `i2cdriver`.


### Switchmode
The [Tasmota command `switchmode`](https://tasmota.github.io/docs/Buttons-and-Switches/#switchmode) commands Tasmota to send an mqtt message when there is a change in state.  This command came in handy when I had an actuator that just needed on/off (like a power switch as the name implies).
```
switchmode1 15
switchmode2 15
```
(github_compile)=
### Compile Tasmota with GitPod

To add a sensor to the build or debug, you'll want to get into VS Code and play around with the code.

- This video will get you started compiling using GitPod [Compiling your own custom Tasmota on the web - No installs, no coding!](https://www.youtube.com/watch?v=vod3Woj_vrs).
- follow the directions on the [Tasmota Compiling page](https://tasmota.github.io/docs/Compile-your-build/).  Assume GitPod.
- After building, go into the build_output directory, right-click on `tasmota-sensors.bin.gz` and click to download.
:::{figure} images/tasmota_build_output.jpg
:align: center
:scale: 70

Tasmota Sensors Build Location
:::

- Go to the main Tasmota screen and select Firmware Upgrade.
- Upload the sensor binary and click on Start Upgrade.

(flash_tasmota)=
## Flash Tasmota Onto a Sonoff Plug
We need a way to turn a plug on or off.  For example, mistBuddy uses two Tasmotized plugs.  One turns mistBuddy's fan on and off.  The other turns mistBuddy's Mister on and off.  By Tasmotizing the plugs, other Buddies can send mqtt messages to turn a plug on or off.


The Sonoff S31 (or S31 Lite) can be flashed so that Tasmota is running on our local network. [This YouTube video gives instructions on how to flash Tosmota](https://www.youtube.com/watch?v=9N58uy3ezvA).

ooh! Extra care when soldering.  If not, well...it is way too easy to rip off one of the pads...

Once flashed and rebooted:
- Put the plug back together.
- Set the Module type to Sonoff S31.

:::{figure} images/Tasmota_S31_Config.jpg
:align: center
:scale: 80

Tasmota Sonoff Configuration
:::
- [Configure mqtt](configure_mqtt).  I change the topic to match the Buddy.  E.g.: if it is mistBuddy's fan plug, mistBuddy_fan.  The mister, vaperbuddy_mister.  Snifferbuddy, snifferbuddy.
- [Set the date/time to your date/time](set_date_time).

(wemos_challenges)=
## ESP286/SCD30 Modifications

_I added this section to maintain what I learned with the Wemos D1 + SCD30 Setup_

I fixed a problem with the SCD30 + ESP286 (Wemos D1) not working without a restart.  I couldn't get the Tasmota team to look at it at the time it happened so I fixed it and submitted a PR.  A bit later on, another person had the same challenge.  Wonderfully, arendst pointed out _From the datasheet it needs 2 seconds to power up. The current code doesn't allow this._ (see [PR 15438](https://github.com/arendst/Tasmota/issues/15438)).
This may be unique to the Wemos mini D1 ESP286 (noisy power...?).

After further investigating the Wemos D1 powering and communication with the SCD 30, Arends notes: _As I thought. The Wemos D1 is flakey at power on._ (That's what $1.50 buys us!). _In latest dev there is a new command called SetOption46 0..255 allowing you to stall initialization for 0..255 * 10 milliseconds to let stabilize the local Wemos power. You might want to experiment with values like SO46 10 os SO46 20 for a 100mSec or 200mSec delay. If you own the Adafruit SCD30 you might also want to power the device from 5V as it draws a lot of power when measuring (notice the fainting power led because the wemos LDO just cannot provide enough power for the device. YMMV._

I have not had a challenge running on 3.3V.  Obviously, Arendst knows ALOT so his advice should be kept in mind.

The `SetOptions46` is avalailable in Tasmota 12.1.1

The files I modified include:
- [xsns_42_scd30.ino](https://github.com/arendst/Tasmota/blob/d157b1c5e0639f8ff29eba01fa3c181a01ae211c/tasmota/xsns_42_scd30.ino).  From what I can tell, Tasmota started as an Arduino project.  The interface into (3rd party) sensor code is a .ino file like this one for the scd30.  The current code:
```
void Scd30Detect(void)
{
  if (!I2cSetDevice(SCD30_ADDRESS)) { return; }

  scd30.begin();
```
On the ESP2866 Wemos, the code doesn't get past the initial `if` statement in the scenario when the ESP8266 is powered up.  It does pass when restarting with `restart 1` on the command line.  Most likely, powering up is taking longer on the ESP286 to the point Tasmota is impatient and doesn't wait for the scd30 to be powered up.  I did not debug further to find out how to robustly fix.  I got to a build that "works for me" with simply:
```
void Scd30Detect(void)
{
#ifdef ESP32
  if (!I2cSetDevice(SCD30_ADDRESS)) { return; }
#endif
  scd30.begin();
```
- [tasmota/my_user_config.h](https://github.com/arendst/Tasmota/blob/d157b1c5e0639f8ff29eba01fa3c181a01ae211c/tasmota/my_user_config.h).  For more info on this file see [the Tasmota compiling YouTube video](https://www.youtube.com/watch?v=vod3Woj_vrs).  I changed:
```
#define TEMP_CONVERSION        false             // [SetOption8] Return temperature in (false = Celsius or true = Fahrenheit)
```
to `true` to show temperature readings in celsius.  As the comment states, I could have set this on the command line using [`SetOption8 1`](https://tasmota.github.io/docs/Commands/#setoptions).


