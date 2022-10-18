# Printing
I have an MK3s Prusa Printer.  This page is dedicated to the challenges I faced while printing and what I did to fix it.
## Thermal Runaway
This occasionally happens.  Particularly on prints that have a flat, large surface area.
As pointed out by [Prusa Support](https://help.prusa3d.com/article/thermal-runaway-i3-series_2131), _**Thermal Runaway** is configured to shut down the printer when the temperature drops by more than 15 °C for more than 45 seconds. If the temperature reading doesn't recover in the set time period, the printer will shut down and display the Thermal Runaway error._

Hopefully, lowering the fan temperature will prevent the Thermal Runaway.  Go into the Prusa Slicr app nd search for fan.  Then lower the min/max value.  Prusa recommends lowering to about  min/max of 70.
