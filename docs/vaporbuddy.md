# VaporBuddy
VaporBuddy is a DIY "Smart" Humidifier for a grow tent with optimized features for automation.  It serves as the actuator for VPD Buddy.  When VPD Buddy decides more water vapor is needed, it sends a command to VaporBuddy to start pumping out water vapor.  When VPD Buddy feels there is enough water vaper (based on the ideal VPD), it sends VaporBuddy a command to turn off.

The VaperBuddy Humidifier:
- has a float valve so a water line can be run to the bucket and autofill.
- blasts a significant amount of vapor into the air.
- can be turned on and off by sending mqtt messages over a home's wifi.

I couldn't find anything on the market that fit my needs, hence VaperBuddy.


## Humidifier
:::{figure} images/humidifier.jpeg
:align: center
:scale: 80

DIY Humidifier
:::
### Materials

The materials I used to make the humidifier in the image include:
#### Base Humidifier
- [Storage Tote from Home Depot](https://www.homedepot.com/p/HDX-14-Gal-Tough-Storage-Tote-in-Black-with-Yellow-Lid-SW111/314468098).
- [2 in. PVC Pipe from Home Depot](https://www.homedepot.com/p/JM-EAGLE-2-in-x-10-ft-White-PVC-Schedule-40-DWV-Plain-End-Pipe-531137/100161954).
- [2 in. PVC 90° elbow](https://www.homedepot.com/p/Charlotte-Pipe-2-in-PVC-DWV-90-Degree-Hub-x-Hub-Elbow-PVC003001000HD/203393418).
- Fan from a PC.  We have an electronics parts store near me that has a box full of PC fans.  The one I am using is quite strong, running at 24V.  A Power Supply will also be needed.
- 48V Power Supply
- [Mist maker from Aliexpress](https://www.aliexpress.com/item/3256803543458943.html?spm=a2g0o.order_list.0.0.57dd1802LzMQr6).  After trying out the one I got, I could imagine getting one half the strength.  Someday I'll figure out how to do the back of the envelope calculations to get exactly what I need...but for now I do what I alwasy do, I bumble on!
![aliexpress 12 head mist maker](images/aliexpress12headmister.jpg)
The one I got specifies a 48VDC power source rated at 350W.  Looking at `Power(P) = Voltage(V)*Current(I)`, I'm interested in how much current is needed. I = 350W/48VDC = 7.3 Amps.  Which is a significant amount!  I had a 48V 250W power supply that I am using which works.  In fact, it is overkill for my space!
#### Continuous Fill
- [Float Valve](https://www.youtube.com/watch?v=vmiO6Z_HLCE)
- [1/2" Barb to 1/2 " NPT female connector](https://amzn.to/3yzxlsG) _Note: The connector fittings assumes 1/2" PEX connector to incoming water_.
#### Remotely turn ON/OFF
- Two Sonoff S31 plugs that have been [Tasmotized](https://github.com/solarslurpi/GrowBuddy/blob/main/pages/flashing_SONOFF_S31.md). I bought a [pack of four from Amazon](https://amzn.to/3xnPWYc).
### Build Directions
#### Building the Base and Continuous Fill Features
For the base and continuous fill, get the popcorn ... it's time for a [How To YouTube Video on making a DIY Humidifier](https://www.youtube.com/watch?v=vmiO6Z_HLCE)
#### Building the Remotely turn ON/OFF Feature
To do this, a [Sonoff S31 plug](https://amzn.to/3xnPWYc) needs to be [flashed with Tasmota](flash_Tasmota_sonoff.md).



