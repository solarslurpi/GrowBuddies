# Getting Started
To start, build a SnifferBuddy and a growBuddy.  These are the foundation of the Buddies.  Once these are built and working, air qulity measurements can be evaluated and stored into a database.  SnifferBuddy's air quality measurements will be used by other Buddies like vpdBuddy.  The air quality information includes air temperature, relative humidity, CO2 level, and a light level reading from the SnifferBuddy's photoresistor.


## Build The Core Components
Let's start with the core components:
- [Build the growBuddy Server](growBuddyServer.md)
- [Build SnifferBuddy](beanie_page)
- [Write Python to access SnifferBuddy readings](examples)
## Store SnifferBuddy Readings
Plug in the growBuddy Server and SnifferBuddy.  The growBuddy Server just needs to be in a position that it can participate in the home's wifi.  The SnifferBuddy should hang where you want to know the temperature, etc. of the air.
- Store Readings.  With [this code], we can store not only the air readings from the SnifferBuddy sensor, but also the vpd calculated from the air and
## Graph SnifferBuddy Readings
- Graph SnifferBuddy Readings
## Adjust the Vaper Pressure Deficit (vpd)
Now that the core Buddies are built, we can move on to managing the vpd level.

When adjusting the vpd to the ideal value, the temperature or the humidity could be adjusted.  growBuddy adjusts the humidity but NOT the temperature.

[mistBuddy](mistBuddy) and vpdBuddy work together to adjust the humidity level within  a grow tent.
Once these Buddies are built, move on to build [VPD Buddy](vpdbuddy).