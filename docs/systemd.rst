*******
Systemd
*******
 
 
`systemd <https://en.wikipedia.org/wiki/Systemd>`_ is used to configure when to run the Python scripts.

Useful Learning Resources on Systemd
====================================

I found the following info useful to figure out how to get systemd to do what I want:

- `Intro to systemd video <https://youtu.be/AtEqbYTLHfs?t=147>`_.  
- `Place in the video where using commands starts <https://youtu.be/AtEqbYTLHfs?t=230>`_.
- `systemd on Raspberry Pi documentation <https://www.raspberrypi.org/documentation/linux/usage/systemd.md>`_.
- `Article on how to autorun service using systemd <https://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/>`_.

Setting Up A Python Script to run as a Systemd service
======================================================
1. Set permissions so systemd can execute the script: ``sudo chmod +x {python script}``.  For example, set permissions on  ``soil_moisture_buddy.py`` by ``sudo chmod +x soil_moisture_buddy.py``.
2. Create the systemd service file.
3. Copy the systemd service file to ``/lib/systemd/system``.  ``sudo`` priviledges are need.  For example, ``sudo cp soil_moisture_buddy.service /lib/systemd/system/.``




* copy service file to where systemd expects it to be.  systemd service files are located at ```/lib/systemd/system```.  Once I created my .service file, I copied it there and tried out some of the commands. e.g.: ```sudo happyday-collect.service /lib/systemd/system/.```
* enable the service with ```sudo systemctl enable happyday-collect.service```.
* check to make sure the service has been enabled with ```systemctl is-enabled happyday-collect.service```
* start the service with ```sudo systemctl start happyday-collect.service```.
* check to make sure the service has been started with ```systemctl is-active happyday-collect.service```
See the ```systemd status``` command info below to debug why your service did not start.