# Troubleshooting

# Is mqtt running?
Here's what I just got when I opened a bash terminal and connected to `Gus`:
```
$ mosquitto_sub -t 'test'
Error: Connection refused
```
...sadly it was working so well.  I am thinking a package update might have changed something in the system.  I only wish the error was Connection refused BECAUSE...WHAT I NEED TO KNOW TO FIX...but alas.



# Log files

```
systemctl status manage_vpd
pi@gus:~$ sudo systemctl start manage_vpd
pi@gus:~$ systemctl status manage_vpd
● manage_vpd.service - MistBuddy adjusts the humidifier based on the vpd
     Loaded: loaded (/lib/systemd/system/manage_vpd.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2023-04-06 13:04:08 PDT; 9s ago
   Main PID: 2631 (python)
      Tasks: 2 (limit: 4915)
        CPU: 9.251s
     CGroup: /system.slice/manage_vpd.service
             └─2631 /home/pi/GrowBuddies/.venv/bin/python /home/pi/GrowBuddies/growbuddiesproject/growbuddies/manage_vp>

Apr 06 13:04:09 gus python[2631]:   Ki = 0.1
Apr 06 13:04:09 gus python[2631]:   Kd = 0.1
Apr 06 13:04:09 gus python[2631]:   setpoint = 0.9
Apr 06 13:04:09 gus python[2631]:   output limits = (0, 20)
Apr 06 13:04:09 gus python[2631]:   integral limits = (0, 7)
Apr 06 13:04:09 gus python[2631]:   tolerance = 0.01
Apr 06 13:04:09 gus python[2631]:   tune = False
Apr 06 13:04:09 gus python[2631]: 2023-04-06 13:04:09,651:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/mqtt_>
Apr 06 13:04:09 gus python[2631]: 2023-04-06 13:04:09,775:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/manag>
Apr 06 13:04:17 gus python[2631]: 2023-04-06 13:04:17,681:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/manag>
```
We see the PID is 2631.  This means we can look at the log files:
```
$journalctl _PID=2631
```
Apr 06 13:04:09 gus python[2631]: Callback for mqtt topic cmnd/mistbuddy_fan/POWER  not found.
Apr 06 13:04:09 gus python[2631]: Callback for mqtt topic cmnd/mistbuddy_mister/POWER  not found.
Apr 06 13:04:09 gus python[2631]: 2023-04-06 13:04:09,509:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/mistbuddy_code.py:92  __init__   ...PID settings:
Apr 06 13:04:09 gus python[2631]:   Kp = 361
Apr 06 13:04:09 gus python[2631]:   Ki = 0.1
Apr 06 13:04:09 gus python[2631]:   Kd = 0.1
Apr 06 13:04:09 gus python[2631]:   setpoint = 0.9
Apr 06 13:04:09 gus python[2631]:   output limits = (0, 20)
Apr 06 13:04:09 gus python[2631]:   integral limits = (0, 7)
Apr 06 13:04:09 gus python[2631]:   tolerance = 0.01
Apr 06 13:04:09 gus python[2631]:   tune = False
Apr 06 13:04:09 gus python[2631]: 2023-04-06 13:04:09,651:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/mqtt_code.py:83  on_connect   ...Connected to broker **gus**.  The ClientID is bbmbzdcbna.  The result code is 0
```
The lines:
```
Apr 06 13:04:09 gus python[2631]: Callback for mqtt topic cmnd/mistbuddy_fan/POWER  not found.
Apr 06 13:04:09 gus python[2631]: Callback for mqtt topic cmnd/mistbuddy_mister/POWER  not found.
```
is interesting.



## manage_vpd
vpd is managed by the manage_vpd.service

.. literalinclude:: growbuddiesproject/growbuddies/service_files/manage_vpd.service