# VPDBuddy

## Resources
The term "Vapor Pressure Deficit" is not that obvious to immediately understand (at least for me).  I found these resources helpful to better understand VPD:

- [YouTube video that I found best explained water vapor, temperature's relationship to Relative Humidity and VPD](https://www.youtube.com/watch?v=-bYPGr1TJQY&t=1s).
- [YouTube video introducing InfluxDB](https://www.youtube.com/watch?v=Vq4cDIdz_M8&list=RDCMUC4Snw5yrSDMXys31I18U3gg&index=2).

## What VPDBuddy Does

VPDBuddy works to make sure the [Vapor Pressure Deficit (VPD)](https://en.wikipedia.org/wiki/Vapour-pressure_deficit) is within an "ideal" range.  The source for the ideal range is the [Flu Cultivation Guide](https://github.com/solarslurpi/GrowBuddy/blob/main/docs/FLU-CultivationGuide_Cannabis_WEB_PROOF_01-2020.pdf) . 

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

A  {ref}`SnifferBuddy <snifferbuddy>` sends out CO2, air temp, and relative humidity (RH) readings from within the grow tent to the GrowBuddy Broker running on a Respberry Pi.  The VPDController Python class
- A VPD Controller Python Class running on the GrowBuddy Raspberry Pi.
- A VaporBuddy tied into the grow tent


VPDBuddy ties the:
- CO2, Temp, and RH readings being sent out by.
- VPD Controller Python Class.
-
 sends it's readings to the GrowBuddy mqtt Broker running on a Raspberry Pi.  The Python Class VPDController RTDSFSDFSSDFDESF
