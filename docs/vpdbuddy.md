# VPDBuddy
```
sniffer_dict: {'Time': '2022-10-23T06:37:32', 'ANALOG': {'A0': 7}, 'SCD30': {'CarbonDioxide': 610, 'eCO2': 589, 'Temperature': 68.0, 'Humidity': 58.4, 'DewPoint': 52.8}, 'TempUnit': 'F', 'vpd': 0.8257631298494408, 'seconds_on': 0}
```

## Resources
The term "Vapor Pressure Deficit" is not that obvious to immediately understand (at least for me).  I found these resources helpful to better understand VPD:

- [YouTube video that I found best explained water vapor, temperature's relationship to Relative Humidity and VPD](https://www.youtube.com/watch?v=-bYPGr1TJQY&t=1s).
- [YouTube video introducing InfluxDB](https://www.youtube.com/watch?v=Vq4cDIdz_M8&list=RDCMUC4Snw5yrSDMXys31I18U3gg&index=2).

## What VPDBuddy Does

VPDBuddy works to make sure the [Vapor Pressure Deficit (VPD)](https://en.wikipedia.org/wiki/Vapour-pressure_deficit) is within an "ideal" range.  The source for the ideal range is the [Flu Cultivation Guide](https://github.com/solarslurpi/growBuddy/blob/main/docs/FLU-CultivationGuide_Cannabis_WEB_PROOF_01-2020.pdf) .

```{image} images/vpd_chart.jpg
:align: center
:scale: 70
```

- vegetative state is 0.8 to 0.95
- flower state is 0.96 to 1.15

From Germination until ready for the vegetative state, the plants germinate under a humidity dome.  Once I take off the dome the plants are in a vegetative state.  This is when VPDBuddy starts.

If the ideal VPD values are maintained during vegetative and flowering state, VPDBuddy is doing it's job!


## System Overview

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
 vpdBuddy implements a modified version of [simple-pid](https://github.com/m-lundberg/simple-pid).  Thanks to the initial work of [Brett Beauregard and his Arduino PID controller as well as documentation](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/).  The modification moves the sampling time from the code.  Instead sampling time is defined by the time between receiving snifferBuddy readings via mqtt messages.
 ### Tuning
 I haven't tuned a PID before.  I'm starting by isolating the P (Proportonal Gain) value.  A challenge for vpdBuddy is the PID error is in terms of vpd units.  For example:
 - vpd setpoint = 0.8
 - vpd reading = 1.2
 - the vpd error is -0.4
 The negative error says mistBuddy needs to be turned on for a number of seconds.  But how many seconds?  The vpd error units are mapped into the Kp value such that the output from the PID controller is the number of seconds to turn on mistBuddy. This requires calibration between the seconds to turn mistBuddy on and the vpd error as well as experimentation to determine how agressive to increase the humidity.
 #### Test 1

 ### Understand P
 My goal is to understand the Proportional constant effect.
 #### First Run: Kp = 0.1
I'm expecting an very gradual increase.
 - Set the Kp in [growBuddy_settings.json](https://github.com/solarslurpi/growBuddy/blob/main/code/growBuddy_settings.json) to 0.1.
```
     "PID_settings": {
        "Kp": 0.01,
        "Ki": 0.1,
        "Kd": 0.1
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
