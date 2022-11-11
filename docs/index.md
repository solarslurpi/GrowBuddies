% growBuddy documentation master file, created by
% sphinx-quickstart on Mon Sep 26 14:48:47 2022.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Welcome to growBuddy!
Hello! Thank you for stopping by.

growBuddy is an Open DIY project.

growBuddy Buddies monitor and maintain the best grow experience.

TODO: picture of grow tent with snifferbuddy.  Then to the side a picture of vaporbuddy....

The available features will evolve incrementally over time.  Currently available Buddies:
- [SnifferBuddy](snifferbuddy.md)
:::{figure} images/snifferbuddy_in_growtent_sm.jpg
:align: center
:height: 250

SnifferBuddy in Grow Tent
:::
SnifferBuddy happily hangs around the grow tent sending out air temperature, humidity, CO2, and light level values over a home's wifi.  The readings are picked up by the growBuddy Server. Other Buddies pick up the readings and act on them.  For example, vpdBuddy gets the SnifferBuddy readings, calculates the vpd and then adjusts the water vapor to the ideal vpd.
- growBuddy Server
:::{figure} images/growBuddy_Server.jpg
:align: center
:height: 250

growBuddy Server
:::

The growBuddy Server is either a Raspberry Pi 4 (the green case encloses a Raspberry Pi 4).  Or Raspberry Pi 3 (like the Raspberry Pi 3 enclosed by the purplse case).  It can store the values in a database for later analysis.  It also runs an mqtt broker that routes the messages the buddies send.
- [vpdBuddy](vpdbuddy.md)




growBuddy is an Open DIY project that monitors and adjusts environment variables that affect plant growth within a grow tent.  Currently, growBuddy focuses on controlling an indoor plant's water needs.  Helping plants get the right amount of water - whether the water is in the form of vapor when in the air or liquid in the soil - is difficult to get right.  Besides, watering requires constant - usually daily - attention.  How does that work when I want to go on vacation?  Since I grow in Living Soil (I recommend [KIS BioChar](https://www.kisorganics.com/products/kis-organics-biochar-soil-mix)), growBuddy's solutions focus on growing in soil, but of course aren't constrained to soil based grows.
## Current Solutions
The current solutions (given the focus is on water) are:
- [Vapor Pressure Deficit (VPD)](vpdbuddy)
- [Soil Moisture](SoilMoistureBuddy.md)


Everyone is welcome. I am a care giver to plants.  Five months out of the year, I grow outdoors.  The rest of the time I grow indoors.  It amazes me how much happiness there can be gained by taking care of plants. I find doing programming and hardware projects a wonderful hobby.  I also love learning and it seems to me there is A LOT I can learn.  So [Contact me](mailto:happygrowBuddy@gmail.com) with thoughts, questions, interests.

Once the water needs are dialed in, other areas that will be explored to automate include:
- adjusting the CO2 level to maxima level of CO2 that is higher than is in the air ( TODO ).
- distance light is from canopy based on PPFD ( TODO )
- nutrition deficits ( TODO )
- pest probems ( TODO )
- virus probems ( TODO )
- 3D Printed Microscope to view microbes ( TODO )
- TBD


```{note} Please [Contact me](mailto:happygrowBuddy@gmail.com) with thoughts, questions, interests.
```
See you in the garden!

```{toctree}
:maxdepth: 1

mygrowtent
getting_started
examples
growBuddyServer
snifferbuddy
vaporbuddy
flash_S31
wiring
tasmota
systemd
vpdbuddy
modules
sphinxLearnings
SoilMoistureBuddy
printing
```
