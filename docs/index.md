% growBuddy documentation master file, created by
% sphinx-quickstart on Mon Sep 26 14:48:47 2022.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Welcome to GrowBuddies! {material-regular}`yard;2em;sd-text-success`
Hello, fellow indoor gardeners!

The GrowBuddies project is designed to help geeky gardeners like us maximize the health and enjoyment of our indoor gardens.

::::{grid} 4
:gutter: 2

:::{grid-item-card} SnifferBuddy
:link: snifferbuddy
:link-type: doc

```{image} images/dog.jpg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
Sniffs out temperature, humidity, and CO2.
:::

:::{grid-item-card} MistBuddy
:link: mistbuddy
:link-type: doc
```{image} images/whale.svg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
Maintains the vpd Level.
:::
:::{grid-item-card} SnapBuddy
:link: snapbuddy
:link-type: doc
```{image} images/snapbuddy_og_v.svg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
Snaps a Time Lapse Image.
:::

:::{grid-item-card} Gus
:link: gus
:link-type: doc
```{image} images/hamster.jpg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
Rasp Pi Running Backend Services.
:::
::::


Not only do GrowBuddies make gardening easier and more fun, but they also help ensure that your plants are healthy and happy.

Stay tuned for more updates. In the meantime, happy gardening!


```{eval-rst}
.. toctree::
   :maxdepth: 1

   getting_started
   gus
   snifferbuddy
   mistbuddy
   snapbuddy
   tasmota
   systemd
   drgrowbuddy
   troubleshooting
```