# flash_Tasmota_sonoff

The purpose of flashing a Sonoff plug with Tasmota is to to send it mqtt messages to turn it on and off.

The Sonoff S31 (or S31 Lite) can be flashed so that Tasmota is running on our local network. [This YouTube video gives instructions on how to flash Tosmota](https://www.youtube.com/watch?v=9N58uy3ezvA).

ooh! Extra care when soldering.  If not, well...it is way too easy to rip off one of the pads...

Once flashed and rebooted:
1. As with any Tasmota device, set up the configuration.  Here we set it up to be an S31:

:::{figure} images/Tasmota_S31_Config.jpg
:align: center
:scale: 80

Tasmota Sonoff Configuration



<p align='left'>2. Set up the mqtt configuration:

:::{figure} images/Tasmota_S31_mqtt.jpg
:align: center
:scale: 80

Tasmota Sonoff mqtt Configuration

In the image, the mqtt broker is the Host, which is the growbuddy broker running on a Raspberry Pi.  The only other thing to change is the Topic.  In this case, the topic is `plug_CO2`  to identify it as the relay plug that is turning on and off the CO2 solenoid.
3. Set up the time.  We set this to PST: `Backlog Timezone 99 ; TimeDST 0,2,03,1,3,-420 ; TimeSTD 0,1,11,1,2,-480`
4. Put the S31 back together.
