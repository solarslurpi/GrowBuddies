(tasmota)=

# Tasmota


## Installation
The easiest way to install Tasmota is using either the Edge or Chrome browser (web install doesn't work using the Brave browser) and go to [Tasmota Install URL](https://tasmota.github.io/install/).  
_Note:  If the USB/COM port can't be identified, the first thing to do is to change cables.  The USB cable might not support data i/o.  If that doesn't work, check the USB driver.  The ESP286 or ESP32 may be using a driver that isn't installed on your Windows PC or Mac._

There are many Tasmota binaries that could be installed.  We want to install the Tasmota Sensors binary.
:::{figure} images/install_tasmota.jpg
:align: center
:scale: 100

Tasmota Install
:::

The install includes connecting to the home wifi.

## Setup
Setup is for things like setting the time between sending mqtt messages, setting the clock to the correct date, time, and timezone, etc.
### Teleperiod
Set up the period between sending the sensor readings over mqtt using the `teleperiod` command.  e.g.:
```
teleperiod 100
```
sets sending readings via mqtt to occur every 100 seconds.
### Local Time


This command set the correct timezone stuff for PST:

Use the web console to configure the Timezone (this shows Pacific time):
```
Backlog Timezone 99 ; TimeDST 0,2,03,1,3,-420 ; TimeSTD 0,1,11,1,2,-480
```
The 99 says to use TimeDST and TimeSTD. Use "time" to check.

[Thank you Craig's Tasmota page](https://xse.com/leres/tasmota/)

Or Keep It Simple and just change the timezone with the command `timezone -8` (see [Tasmota commands](https://tasmota.github.io/docs/Commands/#management)
### i2cscan
Executing `i2cscan` from the console is useful to show you if the i2c sensor is wired correctly.

### Switchmode
The [Tasmota command `switchmode`](https://tasmota.github.io/docs/Buttons-and-Switches/#switchmode) commands Tasmota to send an mqtt message when there is a change in state.  
```
switchmode1 15
switchmode2 15
```

## Creating a Tasmota Binary
This is something you most likely will never do.  But I did to fix a problem with the SCD30 + ESP286 (Wemos D1) not working without a restart.  I couldn't get the team to look at it at the time it happened so I fixed it and submitted a PR.  A bit later on, another person had the same challenge.  Wonderfully, arendst pointed out _From the datasheet it needs 2 seconds to power up. The current code doesn't allow this._ (see [PR 15438](https://github.com/arendst/Tasmota/issues/15438)).  He tried a fix, this didn't seem to work. After investigating further he notes: _As I thought. The Wemos D1 is flakey at power on._ (not uncommon for the ES286 Wemos D1's to be flakey.  That's what $1.50 buys us!).
### SCD 30 + Wemos D1 ESP286
arendst noted _In latest dev there is a new command called SetOption46 0..255 allowing you to stall initialization for 0..255 * 10 milliseconds to let stabilize the local Wemos power. You might want to experiment with values like SO46 10 os SO46 20 for a 100mSec or 200mSec delay. If you own the Adafruit SCD30 you might also want to power the device from 5V as it draws a lot of power when measuring (notice the fainting power led because the wemos LDO just cannot provide enough power for the device. YMMV._

I have not had a challenge running on 3.3V.  Obviously, Arendst knows ALOT so his advice should be kept in mind.

The `SetOptions46` is avalailable in Tasmota 12.1.1


### Resources
- [Compiling your own custom Tasmota on the web - No installs, no coding!](https://www.youtube.com/watch?v=vod3Woj_vrs)

The files I modified include:
- [/tasmota/xsns_42_scd30.ino](https://github.com/arendst/Tasmota/blob/d157b1c5e0639f8ff29eba01fa3c181a01ae211c/tasmota/xsns_42_scd30.ino).  From what I can tell, Tasmota started as an Arduino project.  The interface into (3rd party) sensor code is a .ino file like this one for the scd30.  The current code:
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


