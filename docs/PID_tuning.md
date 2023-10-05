# PID Tuning
(PID_tuning)=
## PID Tuning {material-regular}`settings;1em;sd-text-success`
[**Backgrounder on PID Tuning](https://www.youtube.com/watch?v=tFVAaUcOm4I&t=3s)

PID tuning is a process of finding the "right values" for the Kp, Ki, and Kd gains.  The gains are used to calculate the output of the PID controller. In MistBuddy's case, the output is the number of seconds to turn on the humidifier. The tuning will be unique to each humidifier.
### Time between Readings
The time between readings is set within Tasmota (see the Tasmota section on ["Time Between Readings"](set_time_between_readings)).  I originally had this set to one minute. This was to accommodate longer times the humidifier would be on.  I am now testing getting SnifferBuddy readings every 30 seconds.

The output is used to turn on/off the humidifier.  The gains are set in the `PID_settings` section of the `snifferbuddy_settings.json` file.  To tune the PID, I'll be using [the Ziegler-Nichols method](https://en.wikipedia.org/wiki/Ziegler%E2%80%93Nichols_method).
### Difference Between Day and Night vpd
:::{figure} images/day_night_vpd.jpg
:align: center
:scale: 100

Step 3: Determine Ku and Tu
:::
The image shows the difference between vpd values during the day versus night.  vpd management is turned off when the lights are turned off.  vpd is about managing transpiration.  Transpiration is not happening when the lights are off.  A steep decline in the vpd value happens around 5PM.  This is when the lights turn off.  The vpd value increases again at 5AM when the lights turn on.

### Tuning using the Ziegler-Nichols method
The steps are:
- Set the time between readings to 30 seconds.
- Increment the proportional gain (Kp) until the system oscillates at a constant amplitude. This is called "the ultimate gain (Ku)".
- Rerun the system with the new Kp value. The rerun is to verify the oscillation is stable.
- Measure the oscillation period (Tu).
- Calculate Kp, Ki, and Kd
- Implement the PID controller with the calculated values of Kp, Ki, and Kd.
Test the system and make adjustments as necessary.
#### Set Time Between SnifferBuddy Readings
The time between readings is set within Tasmota (see the Tasmota section on ["Time Between Readings"](set_time_between_readings)).  I originally had this set to one minute. This was to accommodate longer times the humidifier would be on.  I am now testing getting SnifferBuddy readings every 30 seconds. This appears to be working better.
#### Determine the Ultimate Gain (Ku)
The ultimate gain, Ku, is a measure of the maximum closed-loop control response of the system and is used to determine the proportional gain (Kp) of the PID controller.  The ultimate gain is determined by increasing the proportional gain (Kp) until the system oscillates at a constant amplitude.  This is what setting the `tune` variable in the `growbuddies_settings.json` file to `True` does.  When `tune` is set to `True`, each loop of the PID controller increases the proportional gain (Kp) by one.
- Set the influxdb measurement table name in `growbuddies_settings.json`:
```
   "snifferbuddy_table_name": "ziegler_nichols_to_stable",
```
I named the table for this test `ziegler_nichols_to_stable`.  You can name it whatever you want.
- Set `"tune": true` in growbuddies_settings.json:
```
    "PID_settings": {
        "Kp": 250,
        "Ki": 0,
        "Kd": 0,
        "output_limits": [0, 20],
        "integral_limits":[0, 7],
        "tolerance": 0.01,
        "tune": true
    }
```
- Set Kp to a low starting value.
_Note: I had done this.  However, the table in influxdb got corrupted.  Looking at the debug files, I used 250 as the starting value._
- Start `manage_vpd.service`.  Readings will be stored in the measurement table defined within the `"snifferbuddy_table_name"` key in `growbuddies_settings.json`.
   - Evaluate the readings.

:::{figure} images/FindingKu_mistbuddy.jpg
:align: center
:scale: 50

Determine the ultimate Gain (Ku)
:::
While the image is blurry, the plot shows a steady oscillation starting at 13:49:55.  The Ku value is the Kp value at 13:49:55.  I'll use this value as the starting value for Kp in the next step.  The debug record at about this time:
```
Feb 10 13:49:58 gus python[21086]: 2023-02-10 13:49:58,675:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/PID_code.py:189  __call__   ...K values: Kp 361 Ki 0  Kd 0
```
Shows Kp=__Ku=361__.

#### Rerun with Kp set at 361
- Set the influxdb measurement table name in `growbuddies_settings.json`:
```
   "snifferbuddy_table_name": "ziegler_nichols_361",
```
- Set `tune` to false,
- Set the Kp setting to 361:
```
    "PID_settings": {
        "Kp": 361,
        "Ki": 0,
        "Kd": 0,
        "output_limits": [0, 20],
        "integral_limits":[0, 7],
        "tolerance": 0.01,
        "tune": false
    }
```
The results:
:::{figure} images/Kp361.jpg
:align: center

Run with Kp set at 361
:::
The plot shows the os
#### Measure the Oscillation Period (Tu)
The oscillation period (Tu) is the time it takes for the system to complete one oscillation.
#### Step 3: Calculate the Gain Values
:::{figure} images/Tu361_jpg.jpg
:align: center

Oscillation Period (Tu)
:::
Tu = 3 minues = 180 seconds
Ku = 361

Using [the Ziegler-Nichols table for a classic PID controller](https://www.allaboutcircuits.com/projects/embedded-pid-temperature-control-part-6-zieglernichols-tuning/)

|          | Kp       |      Ti       |  Td   |
|----------|----------|:-------------:|------:|
|  P-only  |  Ku/2    |               |       |
|  Pi      |  Ku/2.2  |    Tu/1.2     |       |
|  PID     |  Ku/1.7  |    Tu/2       | Tu/8  |



- Kp = Ku/1.7 = 361/1.7 = 212.35 = 212
- Ti = Tu/2 = 180/2 = 90 seconds
- Td = Tu/8 = 180/8 = 22.5 seconds

Ki = Kp(T/Ti) = 212*(180/90) = 424
Kd = Kp(Td/T) = 212*(22.5/180) = 23

| Gains | Kp    | Ki    | Kd
|-------|:-----:|:-----:|:-----:
|       | 182.4 | 364.8 | 22.8





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

