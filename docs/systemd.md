# Systemd

[systemd](https://wiki.archlinux.org/title/Systemd) is used to configure when to run the Python scripts.

## Useful Learning Resources on Systemd

I found the following info useful to figure out how to get systemd to do what I want:

- [Intro to systemd video](https://youtu.be/AtEqbYTLHfs?t=147).
- [Place in the video where using commands starts](https://youtu.be/AtEqbYTLHfs?t=230).
- [systemd on Raspberry Pi documentation](https://www.raspberrypi.org/documentation/linux/usage/systemd.md).
- [Article on how to autorun service using systemd](https://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/).
- [archlinux systemd documentation](https://wiki.archlinux.org/title/Systemd)
## Setting Up A Python Script to run as a Systemd service

1. Set permissions so systemd can execute the script: `sudo chmod +x {python script}`.  For example, set permissions on  `vpdbuddy_manage.py` by `sudo chmod +x vpdbuddy_manage.py`.
2. Create the systemd service file.  I'm no expert.  So you may want to research using the above learning resources.  Here's an example that worked for me.

```{literalinclude} ../code/examples/vpdbuddy_manage.service
:language: python
:linenos: true
```

3. Copy the systemd service file to `/lib/systemd/system`.  `sudo` priviledges are needed.  For example, `sudo cp vpdbuddy_manage.service /lib/systemd/system/.`
4. Enable the service with `sudo systemctl enable vpdbuddy_manage.service`.
5. Check to make sure the service has been enabled with `systemctl is-enabled vpdbuddy_manage.service`.
6. Start the service with `sudo systemctl start vpdbuddy_manage.service`.
7. Check to make sure the service has been started with `systemctl is-active vpdbuddy_manage.servicee`.  In this example, starting the service failed.  To find out why, try `journalctl -u vpdbuddy_manage.service`.  Here is log lines from one of the services I ran:

```python
Oct 05 14:32:14 growBuddy python3.7[1286]: 2022-10-05 14:32:14,464:DEBUG:\[\]/home/pi/growBuddy/code/growBuddy.py:44  __init__   ...-> Initializing growBuddy class for task readSoilMoisture
Oct 05 14:32:14 growBuddy python3.7[1286]: 2022-10-05 14:32:14,465:DEBUG:\[\]/home/pi/growBuddy/code/growBuddy.py:120  _read_settings   ...-> Reading in settings from growBuddy_settings.json file.
Oct 05 14:32:14 growBuddy python3.7[1286]: 2022-10-05 14:32:14,466:ERROR:\[\]/home/pi/growBuddy/code/growBuddy.py:50  __init__   ......Exiting due to Error: Could not open the settings file named growBuddy_settings.json
Oct 05 14:32:14 growBuddy systemd[1]: soil_moisture_buddy.service: Main process exited, code=exited, status=1/FAILURE
Oct 05 14:32:14 growBuddy systemd[1]: soil_moisture_buddy.service: Failed with result 'exit-code'.
Oct 05 14:32:14 growBuddy systemd[1]: soil_moisture_buddy.service: Service RestartSec=100ms expired, scheduling restart.
Oct 05 14:32:14 growBuddy systemd[1]: soil_moisture_buddy.service: Scheduled restart job, restart counter is at 5.
Oct 05 14:32:14 growBuddy systemd[1]: Stopped growBuddy Soil Moisture Service.
```

Because I started the service with the logging level set to DEBUG, the info in the journal file gives us what we need to fix the problem.  The `growBuddy_settings.json` is not found.  Checking out the current directory the script is in we see: `Oct 05 14:39:33 growBuddy python3.7[1832]: 2022-10-05 14:39:33,709:DEBUG:\[\]/home/pi/growBuddy/code/growBuddy.py:47  __init__   ...--> Current Directory is /`

This is fixed by adding the code in `growBuddy.py` to change to the directory where `growBuddy.py` is located.

```python
# Set the working directory to where the Python files are located.
self.logger.debug(f'--> Current Directory prior to setting to the file location is {os.getcwd()}')
cfd = os.path.dirname(os.path.realpath(__file__))
os.chdir(cfd)
self.logger.debug(f'--> Current Directory is {os.getcwd()}')
```

The reason for the above example is to give a little detail on the approach I take when I can't get the service to start.  I hope it is helpful.
