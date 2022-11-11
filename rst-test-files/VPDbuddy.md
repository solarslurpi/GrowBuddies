# VPDBuddy

VPDBuddy works to make sure the [Vapor Pressure Deficit (VPD)](https://en.wikipedia.org/wiki/Vapour-pressure_deficit) is within an "ideal" range.  The source for the ideal range is the [Flu Cultivation Guide](https://github.com/solarslurpi/growBuddy/blob/main/docs/FLU-CultivationGuide_Cannabis_WEB_PROOF_01-2020.pdf) .  Figure 6 notes an ideal VPD range during the:

```{image} images/vpd_chart.jpg
:align: center
:scale: 70
```

- vegetative state is 0.8 to 0.95
- flower state is 0.96 to 1.15

From Germination until ready for the vegetative state, I put the plants under a humidity dome.  Once I take off the dome the plants are in a vegetative state.  This is when VPDBuddy starts.

If the ideal VPD values are maintained during vegetative and flowering state, VPDBuddy is doing it's job!

## Resources

- [YouTube video that I found best explained water vapor, temperature's relationship to Relative Humidity and VPD](https://www.youtube.com/watch?v=-bYPGr1TJQY&t=1s).
- [YouTube video introducing InfluxDB](https://www.youtube.com/watch?v=Vq4cDIdz_M8&list=RDCMUC4Snw5yrSDMXys31I18U3gg&index=2).

## System Overview

:::{figure} images/vpdbuddy_system_overview.jpg
:align: center
:scale: 100

VPDBuddy System Overview
:::

{ref}`SnifferBuddy <snifferbuddy>` sends it's readings to the growBuddy mqtt Broker running on a Raspberry Pi.  The Python Class VPDController
