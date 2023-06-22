## Playtime {material-regular}`celebration;1em;sd-text-success`
```{note} You must build [SnifferBuddy](snifferbuddy) and [Gus](gus) before playtime can begin.
```
If you have a SnifferBuddy that is sending out MQTT messages and a Gus device that is running an MQTT broker and InfluxDB database,
you can access the command line of the Gus device and type the following command:
```bash
store_readings
```
This will start running the [main function](growbuddies.store_readings.main) in the `store_readings.py` file.

```{eval-rst}
.. automodule:: growbuddies.store_readings
   :members:

.. autoclass:: Callbacks
   :members:
```
## Additional Python Modules

### mqtt_code


```{eval-rst}
.. autoclass:: growbuddies.mqtt_code.MQTTService
   :members:

.. autoclass:: growbuddies.mqtt_code.MQTTClient
   :members: on_message
```
### SnifferBuddyReadings
The snifferbuddy_readings.py module contains the SnifferBuddyReadings class.
```{eval-rst}
.. autoclass:: growbuddies.snifferbuddyreadings_code.SnifferBuddyReadings
   :members:
```
### Settings
The settings_code.py module efficiently retrieves and validates parameter input from the growbuddy_settings.json file.
```{eval-rst}
.. autoclass:: growbuddies.settings_code.Settings
   :members:
```

## Useful Raspberry Pi Stuff

(raspi-nowifi)=
### Installed Raspberry Pi But Cannot SSH
You've verified Gus has an IP address.  However, perhaps you accidentally entered the wrong SSID or password for your wifi.  Or you forget to enable SSH.  You can manually configure these options.
- Add "SSH" file to the root of the image.  We do this by opening a terminal on the boot partition and typing `$touch ssh`
- Create the `wpa_supplicant.conf` file : `$touch wpa_supplicant.conf`.  Copy the contents into the file `nano wpa_supplicant.conf`:
```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOURSSID"
    psk="YOURPWD"
}

```
_Note: Multiple wifi networks can be set up by following [this example](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md)_:

```
network={
    ssid="SchoolNetworkSSID"
    psk="passwordSchool"
    id_str="school"
}

network={
    ssid="HomeNetworkSSID"
    psk="passwordHome"
    id_str="home"
}
```

Changing the ssid and psk to match your network.
- Remove the SD-card.
- Put the SD-card into the Rasp-Pi's micro-SD port.
- Power up the Rasp Pi.  Hopefully wireless is working!


### Using Rsync
Rsync is a very useful utility on the Raspberry Pi.  I document my use here because I keep forgetting
how to use it.  Currently, I am on a Windows PC.  The challenge is to start a Bash session in the right directory.
- open Explorer, go to the directory to use rsync, and type in bash in the text field for the file path.

:::{figure} images/explorer_with_bash.jpg
:align: center
:scale: 100

Getting to Bash Command Line Through Explorer
:::

A wsl window will open at this location.
```
sudo rsync -avh pi@gus:/home/pi/mydata.zip  .

```
### Change Text
From within a directory within multiple files:
```
find /path -type f -exec sed -i 's/oldstr/newstr/g' {} \;
```
### OSError: [Errno 98] Address already in use

#### Find the ProcessID

Using the command: `netstat -tulnp | grep :8000`
```
 pi@gus:~/gus $
pi        2465  0.2  0.4  25956 17520 pts/0    T    09:31   0:00 /home/pi/gus/py_env/bin/python /home/pi/gus/py_env/bin/sphinx-autobuild docs docs/_build/html
pi        2641  0.0  0.0   7344   508 pts/0    S+   09:34   0:00 grep --color=auto sphinx-autobuild
```
The PID we are interested in is 2465.
#### Kill the Process
Onto the kill command, which needs sudo privileges.
```
pi@gus:~/gus $ sudo kill -9 2465
[1]+  Killed                  sphinx-autobuild docs docs/_build/html  (wd: ~/gus/docs)
(wd now: ~/gus)
```
### Check which Python is in Use
It's best practice to run Python code in a virtual environment.  To check to see which interpreter is running:
```
py_env) pi@gus:~/growbuddies $ python
Python 3.7.3 (default, Jan 22 2021, 20:04:44)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> sys.executable
'/home/pi/growbuddies/py_env/bin/python'
```
### Check Rasp Pi OS Version stuff
```
(py_env) pi@gus:~/growbuddies/growbuddies-project $ uname -a
Linux gus 5.10.103-v7l+ #1529 SMP Tue Mar 8 12:24:00 GMT 2022 armv7l GNU/Linux

(py_env) pi@gus:~/growbuddies/growbuddies-project $ cat /etc/debian_version
10.13

(py_env) pi@gus:~/growbuddies/growbuddies-project $ cat /etc/rpi-issue
Raspberry Pi reference 2021-12-02
```
```{note} Debian 10 is Buster.  Debian 11 is Bullseye.
```
### Ignore a Page
If you don't want to include a document in the toctree, add :orphan: to the top of your document to get rid of the warning.

This is a File-wide metadata option. Read more from the [Sphinx documentation](https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html#file-wide-metadata).

### Packaging
There is so much history with Python.  Resource: [Python packaging](https://realpython.com/pypi-publish-python-package).

## Useful InfluxDB Stuff
### Drop all measurements
within a database:
```
DROP SERIES FROM /.*/
```