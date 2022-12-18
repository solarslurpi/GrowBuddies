I use [systemd](https://en.wikipedia.org/wiki/Systemd) to run the python scripts:
* start and run the python script that listens for RFM69 data packets from a moisture puck and stores in a database
* wake up at 5AM and run a python script that creates email messages to me and my husband about whether or not we should water our plants.

The systemd services include:
* [happyday-collect.service](https://github.com/BitKnitting/should_I_water/blob/master/Rasp_Pi_2018/should_i_water/happyday-collect.service) - Listen for RFM69 moisture packets coming in from a Moisture Puck.  When a reading comes in, store it in the database.
* [happyday-email.service](https://github.com/BitKnitting/should_I_water/blob/master/Rasp_Pi_2018/should_i_water/happyday-email.service) and [happyday-email.timer](https://github.com/BitKnitting/should_I_water/blob/master/Rasp_Pi_2018/should_i_water/happyday-email.timer) - Send an email at 5AM every day with the "should i water" info in the database.  The moisture pucks should be sending readings in at 4AM.

 Being new to systemd, I found the following info useful to figure out how to get systemd to do what I want:
* [Intro to systemd video](https://youtu.be/AtEqbYTLHfs?t=147).
  * [Place in the video where using commands starts](https://youtu.be/AtEqbYTLHfs?t=230).
* [systemd in Raspberry Pi documentation](https://www.raspberrypi.org/documentation/linux/usage/systemd.md)
* [Article on how to autorun service using systemd](https://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/).
# Make sure to...
* set permissions so systemd can execute the script: ```sudo chmod +x {python script}```
* copy service file to where systemd expects it to be.  systemd service files are located at ```/lib/systemd/system```.  Once I created my .service file, I copied it there and tried out some of the commands. e.g.: ```sudo cp happyday-collect.service /lib/systemd/system/.```
* enable the service with ```sudo systemctl enable happyday-collect.service```.
* check to make sure the service has been enabled with ```systemctl is-enabled happyday-collect.service```
* start the service with ```sudo systemctl start happyday-collect.service```.
* check to make sure the service has been started with ```systemctl is-active happyday-collect.service```
See the ```systemd status``` command info below to debug why your service did not start.


# Useful Commands
I found the following commands the most useful as I was working with systemd.  I executed them from within an ssh connection to my Raspberry Pi:

* ```systemctl list-units | grep .service``` - lists all the current services running.  I like to get a bigger picture on what's running on my Raspberry Pi.
* ```systemctl status happyday-collect.service```- checks the status of a service.
* ```journalctl _PID=561``` - where the process ID will vary based on the system status.  This command is useful when my service failed to start (i.e.: checked this with ```systemctl status ...```) and got back a failed state, e.g.:
```
 $ systemctl status happyday-collect.service
happyday-collect.service - Collect moisture readings.
   Loaded: loaded (/lib/systemd/system/happyday-collect.service; enabled; systemvendor preset: enabled)
   Active: failed (Result: exit-code) since Wed 2018-04-25 10:52:43 PDT; 49s ago
  Process: 561 ExecStart=/usr/bin/python3 /home/pi/RFM69_Pi/rcv_store_measurements.py (code=exited, status=1/FAILURE)
 Main PID: 561 (code=exited, status=1/FAILURE)
```
The status feedback tells me this service is enabled (i.e.: it will start when the system boots).  However, the service couldn't be started.  The process ID is 561...

* ```journalctl -u happyday-collect.service --since today``` - check for errors or other messages related to systemd's running of a service.  (Note: see [this post on systemd journaling](https://www.digitalocean.com/community/tutorials/how-to-use-journalctl-to-view-and-manipulate-systemd-logs).
* ```sudo systemctl disable happyday-collect.service``` - use disable or enable to change whether the service starts when the system boots.  ```sudo``` is used when changing / manipulating services.
* ```sudo systemctl stop happyday-collect.service``` - use stop or start to stop/start the service.
* ```sudo systemctl daemon-reload``` - run after making a change to the .service file.
* ```sudo systemctl restart happyday-collect.service``` - run after sending systemctl the daemon-reload command.
```
$ systemctl list-timers
NEXT                         LEFT     LAST                         PASSED       UNIT                         ACTIVATES
Wed 2018-05-02 00:35:40 PDT  11h left Tue 2018-05-01 09:17:51 PDT  3h 42min ago apt-daily.timer              apt-daily.service
Wed 2018-05-02 05:00:00 PDT  15h left n/a                          n/a          happyday-email.timer         happyday-email.service
```
# Environment Variables
I rely on Outlook and gmail to send mail for me.  This means I need an account for both.  I don't want the usernames and passwords I use to be readily available on GitHub.  Rather, I rely on systemd's EnvironmentFile directive.  I followed the example in [this stackexchange](https://unix.stackexchange.com/questions/287743/making-environment-variables-available-for-downstream-processes-started-within-a).  I created an env_variables directory on the Raspberry Pi.  Within that directory, I placed a file containing usernames and passwords.  The contents from this directory are not copied to GitHub.
# Run Service at Specific Time
I want the morning watering email to go out every day at 5AM.  I use a systemd timer.  As noted [here](https://wiki.archlinux.org/index.php/Systemd/Timers):
_Timers are systemd unit files with a suffix of .timer. Timers are like other unit configuration files and are loaded from the same paths but include a [Timer] section which defines when and how the timer activates._

_For each .timer file, a matching .service file exists (e.g. foo.timer and foo.service). **The .timer file activates and controls the .service file. The .service does not require an [Install] section as it is the timer units that are enabled**._

I enabled/activated (started) the [happyday-email.timer unit](https://github.com/BitKnitting/should_I_water/blob/master/Rasp_Pi_2018/should_i_water/happyday-email.timer).  That tells systemd to start up the [happyday-email.service](https://github.com/BitKnitting/should_I_water/blob/master/Rasp_Pi_2018/should_i_water/happyday-email.service).



I decided the best way to do this is to add a systemd timer file as described in [this post](https://www.certdepot.net/rhel7-use-systemd-timers/).

