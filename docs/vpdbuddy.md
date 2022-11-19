
:::{div}
<img src="images/whale_misty.svg" class="sd-avatar-md sd-border-3">
:::

# whaleBuddy
whaleBuddy maintains the ideal [vpd level](https://www.canr.msu.edu/uploads/resources/pdfs/vpd-vs-rh.pdfs) identified in [the vpd chart](vpd_chart) by happily blowing mist through it's airhole for the right amount of time.  The method whaleBuddy uses to determine how many seconds to turn on sending mist uses a [PID controller](https://en.wikipedia.org/wiki/PID_controller).

whaleBuddy consists of:
- It's body. whaleBuddy's body
It runs as a [systemd service](https://wiki.archlinux.org/title/Systemd#Basic_systemctl_usage) on a Raspberry Pi running the GrowBuddy service.  Configuration settings are in `growbuddy_settings.json`.

## Resources
I found these resources helpful in my learnings.
### vpd
The term "Vapor Pressure Deficit" is not that obvious to immediately understand (at least for me).  I found these resources helpful to better understand VPD:

- [YouTube video that I found best explained water vapor, temperature's relationship to Relative Humidity and VPD](https://www.youtube.com/watch?v=-bYPGr1TJQY&t=1s).
- [YouTube video introducing InfluxDB](https://www.youtube.com/watch?v=Vq4cDIdz_M8&list=RDCMUC4Snw5yrSDMXys31I18U3gg&index=2).
### PID controller
- [Udemy course](https://www.udemy.com/course/pid-controller-with-arduino/).  While the course notes arduino as the cpu/IDE, what I liked was the intuitive simplicity of this course.  For example, it is pointed out if we just use the P term there is a steady state error, etc.
-  [Brett Beauregard documentation on his PID](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/). whaleBuddy uses a modification of the [simple-pid](https://github.com/m-lundberg/simple-pid) library, which was a port of this work (see [PID]).  A reason to love and support the Open Source Community.

(vpd_chart)=
## VPD Chart

The source for the ideal range is the [Flu Cultivation Guide](https://github.com/solarslurpi/growBuddy/blob/main/docs/FLU-CultivationGuide_Cannabis_WEB_PROOF_01-2020.pdf) .  vpdBuddy gets the ideal vpd levels from the `growbuddy_settings.json` file.

```{image} images/vpd_chart.jpg
:align: center
:scale: 70
```

- vegetative state is 0.8 to 0.95
- flower state is 0.96 to 1.15

From Germination until ready for the vegetative state, the plants germinate under a humidity dome.  Once I take off the dome the plants are in a vegetative state.  This is when VPDBuddy starts.

If the ideal VPD values are maintained during vegetative and flowering state, VPDBuddy is doing it's job!


## vpdBuddy System Overview

:::{figure} images/vpdbuddy_system_overview.jpg
:align: center
:scale: 100

VPDBuddy System Overview
:::

A  [snifferBuddy](snifferBuddy) sends out CO2, air temp, and relative humidity (RH) readings from within the grow tent to the growBuddy Broker running on a Respberry Pi.  The VPDController Python class
- A VPD Controller Python Class running on the growBuddy Raspberry Pi.
- A mistBuddy tied into the grow tent


VPDBuddy ties the:
- CO2, Temp, and RH readings being sent out by.
- VPD Controller Python Class.
-
 sends it's readings to the growBuddy mqtt Broker running on a Raspberry Pi.  The Python Class VPDController

 ## Tuning the PID
 ### PID Python Code
 vpdBuddy implements a modified version of [simple-pid](https://github.com/m-lundberg/simple-pid).  Thanks to the initial work of [Brett Beauregard and his Arduino PID controller as well as documentation](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/).  The modification uses the time between mqtt messages as the (fairly) consistent sampling time instead of the system clock.
 ### Tuning
#### Challenges
- The input, setpoint, and error terms are all in floating point units relative to vpd readings.  vpd readings are typically between 0.0 and 2.0.  The output is the number of seconds to turn on mistBuddy.  Thus, the output includes a conversion from vpd (floating point) to number of seconds (integer)
- Spewing out vapor into the air using mistBuddy is imprecise.  Luckily, the vpd does not have to be precise as shown in the [vpd range chart](vpd_chart)

#### Settings
I start with the P value.  Given the vpd in my grow tent with the lights on is around 1.2, I'll use a vpd setpoint of 0.8 to adjust.

For example:
 - vpd setpoint = 0.8
 - vpd reading = 1.2
 - the vpd error is -0.4
 The negative error says mistBuddy needs to be turned on for a number of seconds.  But how many seconds?  The vpd error units are mapped into the Kp value such that the output from the PID controller is the number of seconds to turn on mistBuddy.

 ### Tuning - Starting with P
 I ran two runs with setting just the P gain.  As shown in the two plots below, setting just the P gain gives an output with a steady state error.

 As noted [by a StackOverflow answer](https://softwareengineering.stackexchange.com/questions/214912/why-does-a-proportional-controller-have-a-steady-state-error)

 _The reason for a steady state error with P only is that as your system approaches the set-point the error signal gets smaller and smaller. Your control is Kp times that error signal and eventually the error will be small enough that Kp times the error won't be enough to force it all the way to zero._
 _An Integrator "saves the day" by accumulating the error over time and therefore even the tiniest error will eventually accumulate to something large enough to force the controller to correct for it._

 From these results, I added in a Ki of 0.1.
 ####  JUST P: Kp = 50, Ki = 0, Kd = 0
I'm expecting an very gradual increase.
 - Set the K settings in [growBuddy_settings.json](https://github.com/solarslurpi/growBuddy/blob/main/code/growBuddy_settings.json).
```
     "PID_settings": {
        "Kp": 50.0,
        "Ki": 0.0,
        "Kd": 0.0
    }
```
- Add `sniferbuddy_table_name` input when instantiating a vpdBuddy instance in the [vpdbuddy_manage.py](https://github.com/solarslurpi/growBuddy/blob/main/code/examples/vpdbuddy_manage.py).  This will store the snifferBuddy readings into the snifferBuddy measurement table of the growBuddy influxdb database.
```
def main():
    vpdbuddy = vpdBuddy(vpd_values_callback=vpd_values_callback, manage=True, snifferbuddy_table_name="snifferbuddy")
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

vpdBuddy Kp=50, Ki=0, Kd=0
:::
### JUST P: Kp=25, Ki=0, Kd=0

:::{figure} images/grafana_vpd_08_25_0_0.jpg
:align: center
:scale: 60

vpdBuddy Kp=25, Ki=0, Kd=0
:::

### PI: Kp=45, Ki=0.1, Kd=0
```
PID(Kp=45, Ki=0.1, Kd=0, setpoint=0.8, sample_time=0.01, output_limits=(None, None), auto_mode=True, proportional_on_measurement=False, error_map=None, mqtt_time=True)
```

:::{figure} images/grafana_vpd_08_45_01_0.jpg
:align: center
:scale: 60

vpdBuddy Kp=45, Ki=0.1, Kd=0
:::

#### Kp=45, Ki=0.1, Kd=0.1
```
PID(Kp=45, Ki=0.1, Kd=0.1, setpoint=0.8, sample_time=0.01, output_limits=(None, None), auto_mode=True, proportional_on_measurement=False, error_map=None, mqtt_time=True)
```
:::{figure} images/grafana_vpd_08_45_01_01.jpg
:align: center
:scale: 60

vpdBuddy Kp=45, Ki=0.1, Kd=0.1
:::
Woops!  mistBuddy stopped working for a bit and...as expected...

#### Kp=40, Ki=0.1, Kd=0.01
```
PID(Kp=45, Ki=0.1, Kd=0.1, setpoint=0.8, sample_time=0.01, output_limits=(None, None), auto_mode=True, proportional_on_measurement=False, error_map=None, mqtt_time=True)
```
:::{figure} images/grafana_vpd_08_40_01_001.jpg
:scale: 60

vpdBuddy Kp=40, Ki=0.1, Kd=0.01
:::

#### Kp=43, Ki=0.1, Kd=0
:::{figure} images/grafana_vpd_08_43_01_0.jpg
:scale: 60

vpdBuddy Kp=43, Ki=0.1, Kd=0
:::

#### Kp=43, Ki=0.1, Kd=0.1
:::{figure} images/grafana_vpd_08_43_01_01.jpg
:scale: 60

vpdBuddy Kp=43, Ki=0.1, Kd=0
:::

## Starting the vpdBuddy Service
- Follow the steps to enable the