# Getting Started
Let's go through building and running the core components - [SnifferBuddy](snifferbuddy) and [Gus](gus).
:::{div}
<img src="https://docs.google.com/drawings/d/e/2PACX-1vTjks0iZHIZyD4VEdOo01_se0jn_CgJu9JUCee-rUhXBmFfykmObBkpqSUFBkOvnIdisiIzygPvDeZa/pub?w=984&amp;h=474&amp;align=middle">
:::

Once these are built and running, we can:
- Store SnifferBuddy readings into an influxdb database.
- Plot the readings using Grafana.
These are the foundation of the Buddies.  Once these are built and working, air quality measurements can be evaluated and stored in a database.  SnifferBuddy's air quality measurements will be used by other Buddies like vpdBuddy.  The air quality information includes air temperature, relative humidity, CO2 level, and a light level reading from SnifferBuddy's photoresistor.


## Build The Core Components
Let's start with the core components.  Each Buddy has its area of documentation.
1. [Build Gus](gus)
2. [Build SnifferBuddy](snifferbuddy)

