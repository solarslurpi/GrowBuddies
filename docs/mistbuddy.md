(mistbuddy_doc)=

# MistBuddy
:::{div}
<img src="images/whale.svg" class="sd-avatar-md sd-border-3">
:::

```{warning} MistBuddy is Under Construction!
```
## About {material-regular}`question_mark;1em;sd-text-success`
:::{div}
<img src="https://docs.google.com/drawings/d/e/2PACX-1vQnc4PqB6jgMzFOIMZqWpJ1dFUUdEsrNfNtB4n6q8jmW68PfWBYvIfANB0gqFjMqUh3rn0Cm_YLLthx/pub?w=984&amp;h=474&amp;align=middle">
:::


MistBuddy has a whale of a good time maintaining a grow tent's ideal [vpd level](https://www.canr.msu.edu/floriculture/uploads/files/Water%20VPD.pdf).   When the vpd level is too high, MistBuddy spouts out mist through her airhole for **just** the right amount of time.  When the vpd is too low or just right, MistBuddy shuts off until the vpd level is higher than the ideal vpd level (also known as the setpoint).

```{note} Our indoor gardening environment is climate controlled.  The temperature with the LED lights on is around 75&#8457;.  While vpd is dependent on both temperature and humidity, MistBuddy only changes the humidity to adjust the vpd.
```

### MistBuddy's Body

MistBuddy's body is a DIY humidifier optimized for the growBuddies environment.  Here's the one I built:

```{figure} images/MistBuddy.jpeg
:align: center
:scale: 20

MistBuddy Outer Shot
```

```{figure} images/MistBuddy_inside.jpeg
:align: center
:scale: 20

MistBuddy Inside Shot
```
Mistbuddy dispenses vapor at the end of the PVC tube by turning on a 12-head mister.  Water comes into the tub through a connection with our house's plumbing.  The water is kept to a constant level in the tub by a float valve.


### MistBuddy's Software
The MistBuddy Python code runs on [Gus](gus) as a [Systemd service](systemd).  The code flow is:

Keep doing until told to stop:
- Get vpd values by subscribing to [SnifferBuddy](snifferbuddy) messages.
- When a vpd value comes in, send it to the PID controller.   MistBuddy implements a modified version of the [simple-pid](https://github.com/m-lundberg/simple-pid) package.  Thanks to the initial work of [Brett Beauregard and his Arduino PID controller as well as documentation](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/).  The modification uses the time between mqtt messages as the (fairly) consistent sampling time instead of the system clock.
- The PID controller returns how many seconds to turn the DIY humidifier on.
- Turn the DIY humidifier on for the number of seconds returned.

```{note} The ideal vpd levels come from [the vpd chart](vpd_chart).
```

## Let's Make One {material-regular}`build;1em;sd-text-success`

```{button-link} https://github.com/solarslurpi/GrowBuddies/discussions
:outline:
:color: success

 {octicon}`comment;1em;sd-text-success` Comments & Questions
```

```{attention}
Before MistBuddy can run, the following must happen:
1. There must be a working SnifferBuddy and Gus.
2. The steps below must be completed.
```
### 1. Gather The Materials

The materials I used to make the humidifier in the image include:
- A [Storage Tote from Home Depot](https://www.homedepot.com/p/HDX-14-Gal-Tough-Storage-Tote-in-Black-with-Yellow-Lid-SW111/314468098).
- [2 in. PVC Pipe from Home Depot](https://www.homedepot.com/p/JM-EAGLE-2-in-x-10-ft-White-PVC-Schedule-40-DWV-Plain-End-Pipe-531137/100161954).
- [2 in. PVC 90° elbow](https://www.homedepot.com/p/Charlotte-Pipe-2-in-PVC-DWV-90-Degree-Hub-x-Hub-Elbow-PVC003001000HD/203393418).
- [Waterproof IP67 12v Fan](https://amzn.to/3WgADKK).  The first fan I used was a leftover fan.  It broke pretty soon.  I got this fan.  It is more powerful and waterproof.  It also has a nice, solid connector connecting the power source to the fan.  What's not to like?
- [Power source for the fan](https://amzn.to/3VT9pKp).  This is a very compact power source that has the right connector to connect the fan.
- [Mist maker from Aliexpress](https://www.aliexpress.com/item/3256803543458943.html?spm=a2g0o.order_list.0.0.57dd1802LzMQr6).  I did not do any measurements to determine the ideal amount of misters.  Perhaps less can be used.
- Power source for the mist maker.   The    [Aliexpress listing](https://www.aliexpress.us/item/3256803543458943.html) notes a power source of 350W and 48V is needed.  I have an old power supply that is less powerful than this that works fine.
:::{figure} images/power__supply.jpeg
:align: center
:scale: 30

250W 48V
:::
- [Float Valve](https://www.youtube.com/watch?v=vmiO6Z_HLCE) to stop the constantly running water line from filling the tub.
- [1/2" Barb to 1/2 " NPT female connector](https://amzn.to/3yzxlsG) _Note: The _connector fittings _assume_ 1/2"_ PEX connector to incoming water_.
- Two [Sonoff [S31 plugs](https://amzn.to/3xnPWYc) need to be [flashed with Tasmota](flash_tasmota).  One plug is used to turn on/off the 48V power supply for the mister.  The other is to turn on/off the power supply to the fan.
:::{figure} images/sonoffplugs.jpeg
:align: center
:scale: 50

Tasmotized Sonoff Plugs Ready for Action
:::

### 2. Build
#### Base and Continuous Fill
For the base and continuous fill, get the popcorn ... it's time for a [How To YouTube Video on making a DIY Humidifier](https://www.youtube.com/watch?v=vmiO6Z_HLCE).

The water level for the float valve is 1 cm above the sensor line.

:::{figure} images/mister_water_level.jpg
:align: center
:scale: 80

Mister Water Level
:::
#### Tasmotized Plugs
MistBuddy sends mqtt messages to the mister and fan plugs.  The plugs run Tasmota which handles all the mqtt messages.  Two [Sonoff [S31 plugs](https://amzn.to/3xnPWYc) need to be [flashed with Tasmota](flash_tasmota).

## Software {material-regular}`terminal;1em;sd-text-success`
The core component of the MistBuddy software is the [PID controller](https://en.wikipedia.org/wiki/PID_controller).  MistBuddy implements a modified version of [simple-pid](https://github.com/m-lundberg/simple-pid).  Thanks to the initial work of [Brett Beauregard and his Arduino PID controller as well as documentation](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/).  The modification uses the time between mqtt messages as the (fairly) consistent sampling time instead of the system clock.

The job of a PID controller is to keep a value at a setpoint defined by the user.  In this case, the setpoints MistBuddy cares about are in the `growbuddy_settings.json` file:
```
    "vpd_setpoints": {
        "veg": 0.9,
        "flower": 1.0
    }
```

This sets the ideal vpd in the vegetative stage to 0.9 and the flowering stage to 1.0.

I came up with the following values for Kp, Ki, Kd after runs I made in my attempt to tune the PID controller:
```
    "PID_settings": {
        "Kp": 43,
        "Ki": 0.1,
        "Kd": 0.1,
        "output_limits": [0, 30]
    }
```
Using 43 for the Kp gain includes converting from vpd errors that are in tenths values to several seconds to turn on the humidifier.


### Let's Play
```{button-link} https://github.com/solarslurpi/GrowBuddies/discussions
:outline:
:color: success

 {octicon}`comment;1em;sd-text-success` Comments & Questions
```
The GrowBuddies package includes a script, `manage-vpd`, that works tirelessly to maintain the vpd level given a vegetative setpoint vpd of 0.9 and a flowering setpoint vpd of 1.0.s

### Tuning the PID


The following discusses my tuning steps.
```{note} For tuning purposes, I used a value of 0.8 for the vpd setpoint.  This was because I knew the vpd in the grow tent was about 1.2, which makes the PID controller kick into action to adjust the vpd down.
```

#### Challenges
- The input, setpoint, and error terms are all in floating point units relative to vpd readings.  vpd readings are typically between 0.0 and 2.0.  The output is the number of seconds to turn on MistBuddy.  Thus, the output includes a conversion from vpd (floating point) to the number of seconds (integer)
- Spewing out vapor into the air using MistBuddy is imprecise.  Luckily, the vpd does not have to be precise as shown in the [vpd range chart](vpd_chart)

#### Getting Started

I start turning by just focusing on the P value.  Given the vpd in my grow tent with the lights on is around 1.2, I'll use a vpd setpoint of 0.8 to adjust.

For example:
 - vpd setpoint = 0.8
 - vpd reading = 1.2
 - the vpd error is -0.4
 The negative error says MistBuddy needs to be turned on for several seconds.  But how many seconds?  The vpd error units are mapped into the Kp value such that the output from the PID controller is the majority of the number of seconds to turn on MistBuddy.  If Kp = 43 then MistBuddy turns on the humidifier for abs(43 * -0.4) = 17 seconds.

 #### Starting with P
 I ran two runs with setting just the P gain.  As shown in the two plots below, setting just the P gain gives an output with a steady state error.

 As noted [by a StackOverflow answer](https://softwareengineering.stackexchange.com/questions/214912/why-does-a-proportional-controller-have-a-steady-state-error)

 _The reason for a steady state error with P only is that as your system approaches the set-point the error signal gets smaller and smaller. Your control is Kp times that error signal and eventually the error will be small enough that Kp times the error won't be enough to force it all the way to zero._
 _An Integrator "saves the day" by accumulating the error over time and therefore even the tiniest error will eventually accumulate to something large enough to force the controller to correct for it._

 From these results, I added in a Ki of 0.1.
 #####  Kp = 50
I'm expecting an very gradual increase.
 - Set the K settings in [growBuddy_settings.json](https://github.com/solarslurpi/growBuddy/blob/main/code/growBuddy_settings.json).
```
     "PID_settings": {
        "Kp": 50.0,
        "Ki": 0.0,
        "Kd": 0.0
    }
```
- Add `sniferbuddy_table_name` input when instantiating a MistBuddy instance in the [vpdbuddy_manage.py](https://github.com/solarslurpi/growBuddy/blob/main/code/examples/vpdbuddy_manage.py).  This will store the snifferBuddy readings into the snifferBuddy measurement table of the growBuddy influxdb database.
```
def main():
    vpdbuddy = MistBuddy(vpd_values_callback=vpd_values_callback, manage=True, snifferbuddy_table_name="snifferbuddy")
    vpdbuddy.start()
```
- [Set the time between mqtt messages](set_time_between_readings) to be one minute.
- Run vpdbuddy_manage.py.
```
(pyenv) $ python code/examples/vpdbuddy_manage.py
```
- View a graph.
#### JUST P: Kp=50, Ki=0, Kd=0
```
PID(Kp=50, Ki=0, Kd=0, setpoint=0.8, sample_time=0.01, output_limits=(None, None), auto_mode=True, proportional_on_measurement=False, error_map=None, mqtt_time=True)
```

:::{figure} images/grafana_vpd_08_50_0_0.jpg
:align: center
:scale: 60

MistBuddy Kp=50, Ki=0, Kd=0
:::
### JUST P: Kp=25, Ki=0, Kd=0

:::{figure} images/grafana_vpd_08_25_0_0.jpg
:align: center
:scale: 60

MistBuddy Kp=25, Ki=0, Kd=0
:::

### PI: Kp=45, Ki=0.1, Kd=0
```
PID(Kp=45, Ki=0.1, Kd=0, setpoint=0.8, sample_time=0.01, output_limits=(None, None), auto_mode=True, proportional_on_measurement=False, error_map=None, mqtt_time=True)
```

:::{figure} images/grafana_vpd_08_45_01_0.jpg
:align: center
:scale: 60

MistBuddy Kp=45, Ki=0.1, Kd=0
:::

#### Kp=45, Ki=0.1, Kd=0.1
```
PID(Kp=45, Ki=0.1, Kd=0.1, setpoint=0.8, sample_time=0.01, output_limits=(None, None), auto_mode=True, proportional_on_measurement=False, error_map=None, mqtt_time=True)
```
:::{figure} images/grafana_vpd_08_45_01_01.jpg
:align: center
:scale: 60

MistBuddy Kp=45, Ki=0.1, Kd=0.1
:::
Woops!  MistBuddy stopped working for a bit and...as expected...

#### Kp=40, Ki=0.1, Kd=0.01
```
PID(Kp=45, Ki=0.1, Kd=0.1, setpoint=0.8, sample_time=0.01, output_limits=(None, None), auto_mode=True, proportional_on_measurement=False, error_map=None, mqtt_time=True)
```
:::{figure} images/grafana_vpd_08_40_01_001.jpg
:scale: 60

MistBuddy Kp=40, Ki=0.1, Kd=0.01
:::

#### Kp=43, Ki=0.1, Kd=0
:::{figure} images/grafana_vpd_08_43_01_0.jpg
:scale: 60

MistBuddy Kp=43, Ki=0.1, Kd=0
:::

#### Kp=43, Ki=0.1, Kd=0.1
:::{figure} images/grafana_vpd_08_43_01_01.jpg
:scale: 60

MistBuddy Kp=43, Ki=0.1, Kd=0
:::

## Starting the MistBuddy Service
- Follow the steps to enable the

## Resources
I found these resources helpful in my learning.
### vpd
The term "Vapor Pressure Deficit" is not that obvious to immediately understand (at least for me).  I found these resources helpful to better understand VPD:

- [YouTube video that I found best explained water vapor, temperature's relationship to Relative Humidity and VPD](https://www.youtube.com/watch?v=-bYPGr1TJQY&t=1s).
- [YouTube video introducing InfluxDB](https://www.youtube.com/watch?v=Vq4cDIdz_M8&list=RDCMUC4Snw5yrSDMXys31I18U3gg&index=2).
### PID controller
- [Udemy course](https://www.udemy.com/course/pid-controller-with-arduino/).  While the course notes arduino as the cpu/IDE, what I liked was the intuitive simplicity of this course.  For example, it is pointed out that if we just use the P term there is a steady state error, etc.
-  [Brett Beauregard documentation on his PID](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/). MistBuddy uses a modification of the [simple-pid](https://github.com/m-lundberg/simple-pid) library, which was a port of this work (see [PID]).  A reason to love and support the Open Source Community.

(vpd_chart)=
### VPD Chart

The source for the ideal range is the [Flu Cultivation Guide](https://github.com/solarslurpi/growBuddy/blob/main/docs/FLU-CultivationGuide_Cannabis_WEB_PROOF_01-2020.pdf).  MistBuddy gets the ideal vpd levels from the `growbuddy_settings.json` file.

```{image} images/vpd_chart.jpg
:align: center
:scale: 70
```

- vegetative state is 0.8 to 0.95
- flower state is 0.96 to 1.15

From Germination until ready for the vegetative state, the plants germinate under a humidity dome.  Once I take off the dome the plants are in a vegetative state.  This is when MistBuddy starts.

If the ideal VPD values are maintained during the vegetative and flowering state, MistBuddy is doing its job!

