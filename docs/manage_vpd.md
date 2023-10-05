# Manage VPD Level
manage_vpd is a python script that leverages the SystemD service to call into [MistBuddy](mistbuddy.md) to manage the [vpd](_vpd).
## Before Starting
[The humidifier and Tasmotized plugs](_make_mistbuddy) need to be on with both plugs switched off but listening for MQTT messages.

(_manage_vpd_settings)=
## (Optional) Edit the Settings File
As with [SnifferBuddy](snifferbuddy), [there are settings](_growbuddies_settings) that may need to be changed. Here is the contents of the `growbuddies_settings.json` file:

```{eval-rst}
.. literalinclude:: ../growbuddiesproject/growbuddies/growbuddies_settings.json
   :language: json
   :emphasize-lines: 8-25

```
The properties not highlighted are discussed during [the documentation for storing SnifferBuddy readings](_growbuddies_settings).
The properties that might need to be changed include:

| Property | Purpose |
| -------- | ------- |
| mistbuddy_mqtt | These contain the dictionary of MQTT topics used by MistBuddy.  Unlike SnifferBuddy's<br>snifferbuddy_mqtt property (see [SnifferBuddy's settings](_growbuddies_settings)), MistBuddy only publishes MQTT messages.<br>It does not provide any callbacks. This makes sense because MistBuddy listens for<br>SnifferBuddy's MQTT messages and might turn on or off the power via the<br>MistBuddy MQTT messaging. There is one topic for turning of the power<br>to the fan and one for turning of the power to the mister.

## 3. Install the GrowBuddies Library
If you haven't already, open a terminal within the Python Virtual Environment.
```
pip install growbuddies
```
## 4. Start the manage_vpd Service
If you have a SnifferBuddy that is sending out MQTT messages and a Gus device that is running an MQTT broker and InfluxDB database,
you can access the command line of the Gus device and type the following command:
```bash
.......
```
This will start running the [main function](growbuddies.store_readings.main) in the `store_readings.py` file.

## 5. Run as a SystemD Service
TBD

## 6. manage_vpd Code Walkthrough
```{eval-rst}
.. autofunction:: growbuddies.manage_vpd.main
.. autofunction:: growbuddies.manage_vpd.manage_vpd


```





