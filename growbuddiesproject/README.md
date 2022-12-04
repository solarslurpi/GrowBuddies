# Welcome to the GrowBuddies Library!

Thank you for stopping by.  The GrowBuddies project is yet another Open DIY indoor gardening project.  This project's main goal is to have more fun gardening by buddying up with technology that can help us have a happier gardening experience.


<img src="https://docs.google.com/drawings/d/e/2PACX-1vTjks0iZHIZyD4VEdOo01_se0jn_CgJu9JUCee-rUhXBmFfykmObBkpqSUFBkOvnIdisiIzygPvDeZa/pub?w=984&amp;h=474&amp;align=middle">

The [GrowBuddies documentation](https://growbuddies.readthedocs.io/en/latest/) will guide you in the building of:

- **SnifferBuddy** - SnifferBuddy is a core Buddy.  Inside SnifferBuddy is a [SCD30](https://www.adafruit.com/product/4867)[air quality sensor](https://www.adafruit.com/product/4867)] measuring the air's temperature, humidity, and CO2 level.   There is a photoresistor at the top of SnifferBuddy to indicate whether the grow lights are on or off. The brain behind SnifferBuddy is an ESP286 running [Tasmota firmware](https://tasmota.github.io/docs/About/). The Tasmota software publishes the readings over mqtt to an mqtt broker running on Gus.
- **Gus** - Gus is also a core Buddy.  Gus is a Raspberry Pi 3 or 4 running an mqtt broker, grafana, influxdb, as well as the Buddies services.  He's the Heavy Lifter.

Once SnifferBuddy and Gus are built, air readings coming in from SnifferBuddy can be stored in the influxdb running on Gus as well as plotted using Grafana.  Now that the core is built, other Buddies can be added like:
- **MistBuddy** - MistBuddy is currently being worked on.  MisBuddy automates shooting out vapor when it is determined the [vpd](https://www.canr.msu.edu/floriculture/uploads/files/Water%20VPD.pdf) is too high.  Ah, _now_ the plants can live their best lives!