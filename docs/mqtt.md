# mqtt

mqtt is how the Buddies text message each other. For example, [SnifferBuddy](snifferbuddy.md) sends out (i.e.: publishes in mqtt terminology) over wifi an mqtt message like this:
```
{"Time":"2022-09-06T08:52:59",
  "ANALOG":{"A0":542},
  "SCD30":{"CarbonDioxide":814,"eCO2":787,"Temperature":71.8,"Humidity":61.6,"DewPoint":57.9},"TempUnit":"F"}
}
```
[vpdBuddy](vpdBuddy.md) is listening for messages from SnifferBuddy (i.e.: subscribed to )
We use the mosquitto broker running on a raspberry pi.
## Resources
- [Installing mosquitto on Rasp Pi](https://pimylifeup.com/raspberry-pi-mosquitto-mqtt-server/)
- [mqtt Explorer](http://mqtt-explorer.com/) - this tool helped me figure out the message format for turning on and off the relay in the S3...e.g.: `cmnd/plug_fillerup/POWER` is the topic for the plug I set the mqtt topic to within the mqtt configuration UI on the Tasmota console to  `plug_fillerup`.  The message is then one of `on`, `off`, or `toggle`.
## Installing
It's easiest to follow [one of the many available guides](https://pimylifeup.com/raspberry-pi-mosquitto-mqtt-server/). _Note: I didn't realize the package installer will install mosquitto as a service and start it running: From the article_ `During the installation process, the package manager will automatically configure the Mosquitto server to start on boot.` _I aslo did the systemd service incantations..._
## Configuring
 In order to connect to the mosquitto service, the conf file must be modified.  This doesn't need to happen if everything communicating are Tasmota devices.  However, I also have React Native apps that need to connect over websockets, which is not configured by default.  The best way to add this to the configuration is to  use the `/etc/mosquitto/conf.d/connect.conf file:
```
listener 1883
protocol mqtt

listener 9000
protocol websockets

allow_anonymous true
```
- added `allow_anonymous true` without this, I could not publish from a terminal on Rasp Pi.
- added `listener 9000` and `protocol websockets` with this, a react client cannot connect.  _Note: I arbitrarily use port 9000_
- `carbot.py`: Python app that handles (subscribes) to the 'carbot/move' commands (forward, backward, stop, faster, and slower).
- `carbot.service`: Systemd service file to start and stop carbot.py running.  To use this file, it must be copied.  `sudo cp carbot.service /lib/systemd/system/.`
## Debugging
- __Status__ provides info on whats going on with the carbot service.
- __Log Statements__ are sprinkled throughout `carbot.py` to help in debugging.
- __mosquitto log file__ provides info on the health of the mosquitto service.

### Status
Use `systemctl status carbot` and you will get info such as:
```
● carbot.service - carbot mqtt Script Service
     Loaded: loaded (/lib/systemd/system/carbot.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2021-12-11 06:49:20 PST; 8s ago
   Main PID: 4394 (python3)
      Tasks: 1 (limit: 1597)
        CPU: 641ms
     CGroup: /system.slice/carbot.service
             └─4394 /usr/bin/python3 /home/pi/GrowBuddy/Doctor/carbot/carbot.py

Dec 11 06:49:20 doctorgrowbuddy systemd[1]: Started carbot mqtt Script Service.
Dec 11 06:49:21 doctorgrowbuddy python3[4394]: 2021-12-11 06:49:21,102:DEBUG:starting up!
Dec 11 06:49:21 doctorgrowbuddy python3[4394]: 2021-12-11 06:49:21,159:DEBUG:subscribing
```
We see debug statements are included.

### Log Statements
Additional debug info can be found in the `Journalctl` logfile.  To see the logfiles, notice the PID from the status info (e.g.: 4394 is the PID listed above) and then `Journalctl _PID=4394`
```
$ journalctl _PID=4394
-- Journal begins at Sat 2021-10-30 04:36:50 PDT, ends at Sat 2021-12-11 06:49:21 PST. --
Dec 11 06:49:21 doctorgrowbuddy python3[4394]: 2021-12-11 06:49:21,102:DEBUG:starting up!
Dec 11 06:49:21 doctorgrowbuddy python3[4394]: 2021-12-11 06:49:21,159:DEBUG:subscribing
Dec 11 06:49:21 doctorgrowbuddy python3[4394]: 2021-12-11 06:49:21,160:DEBUG:subscribed
```
There will be additional logging lines when `carbot.py` receives and processes the commands (forward, backward...).

To get the logs into `Journalctl`, `carbot` sends log files to `sys.stdout`.
`carbot.py` sets up logging to be handled by `Journalctl`.
### mosquitto log file
The mosquitto log file is found in `/var/log/mosquitto/mosquitto.log`.  It has records like:
```
1639229562: Config loaded from /etc/mosquitto/mosquitto.conf.
1639229562: Opening ipv4 listen socket on port 1883.
1639229562: Opening ipv6 listen socket on port 1883.
1639229562: Opening websockets listen socket on port 9000.
1639229562: mosquitto version 2.0.11 running
```
## Determining if Device is Sending Messages
[MQTT Last will and Testament](https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/) is an extremely useful feature for detecting when devices go bad.
__By default Tasmota devices set their LWT with a topic of tele/devicename/LWT and a payload of offline when they connect to the broker, and send a message of tele/devicename/LWT and a payload of online as soon as they start.__
MQTT devices continually ping the broker with a keep alive message, if the broker doesn't get these messages it publishes the LWT message, so if you want to know if your device has gone bad, all you need to do is to subscribe to the LWT topic and wait. The article, [MQTT Esentials Page 9](https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/), identifies these states when the mqtt broker publishes the LWT message:

- The broker detects an I/O error or network failure.
- The client fails to communicate within the defined Keep Alive period.
- The client does not send a DISCONNECT packet before it closes the network connection.
- The broker closes the network connection because of a protocol error.

We've gotten OFFLINE messages when:
- The Tasmota device has been restarted.
- The Tasmota device has been unplugged longer than the keep alive time.


issuing the `status 6` command on the Tasmota command line informs us on the mqtt settings for this Tasmota device:
```
 MQT: stat/snifferbuddy/STATUS6 = {"StatusMQT":{"MqttHost":"growbuddy","MqttPort":1883,"MqttClientMask":"DVES_%06X","MqttClient":"DVES_25EEA5","MqttUser":"DVES_USER","MqttCount":1,"MAX_PACKET_SIZE":1200,"KEEPALIVE":30,"SOCKET_TIMEOUT":4}}
 ```
The mqtt info lets us know the mqtt keep alive time is 30 seconds.