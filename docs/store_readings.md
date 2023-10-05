# Store SnifferBuddy Readings
This section assumes you have built both a SnifferBuddy and Gus.  If this is not the case,
::::{grid} 2 2 2 2

:::{grid-item}
:columns: 2
:::

:::{grid-item}
:columns: 4
```{button-ref} make_snifferbuddy
:ref-type: myst
:align: center
:color: success
:shadow:
Make SnifferBuddy
```
:::
:::{grid-item}
:columns: 4
```{button-ref} make_gus
:ref-type: myst
:align: center
:color: success
:shadow:
Make Gus
```
:::
::::
After successfully setting up a SnifferBuddy and a Gus, SnifferBuddy Readings can be stored in the InfluxDB and graphed using Grafana.  The focus here is on storing readings.
(setup_python_env)=
## 1. Create a Python Programming Environment
My Python programming environment consists of Windows PC, VS Code, and venv.  I typically create a folder on my Windows PC.  Also, with Git installed,  I like to use Git Bash for my command line over WSL or PowerShell.  The only challenge for me is when activating the virtual environment, it's
```
source .venv/Source/activate
```
instead of
```
source .venv/bin/activate
```
(assuming you installed the virtual environment as)
```
python -m venv .venv
```
### Optional: Using Git Bash
Ignore this part if you are comfortable with your own command line tool (e.g.: PowerShell, Bash, WSL...).  To use Git Bash,
- In VS Code, press down on ctl-shift-P.
- Type in Select default profile.
- Choose Git Bash.
- open a Terminal Window.
- Check if Git Bash is the default terminal.  If not, check the pulldown to choose Git Bash.

(_growbuddies_settings)=
## 2. Edit The Settings File
Below is the contents of `growbuddies_settings.json`. The settings file contains the configurable properties for running the GrowBuddies.

```{eval-rst}
.. literalinclude:: ../growbuddiesproject/growbuddies/growbuddies_settings.json
   :language: json
   :emphasize-lines: 1-7

```
The properties that might need to be changed include:

| Property | Purpose |
| -------- | ------- |
| hostname | This is the name given to the Raspberry Pi during [installation of the Raspberry OS](_install_pi).<br>The settings file assumes the name of the Raspberry Pi is gus. |
| log_level | The GrowBuddies are backed by extensive logging. By default the logging level is `DEBUG`.<br>Standard Python logging is used. The log_level can be `DEBUG`, `INFO`, `WARNING`, `ERROR`,<br>`CRITICAL`.  Setting to `DEBUG` will include all log entries. |
| db_name | InfluxDB needs a database created in order to store the SnifferBuddy readings within it.<br>By default, the db_name is `gus`.
| snifferbuddy_table_name | The name of the table within the InfluxDB database named by `db_name` that will hold the SnifferBuddy readings.
| snifferbuddy_mqtt | The name of the two callback functions. `snifferbuddy/reading` is called when a reading is available.  `snifferbuddy/lwt` is called when a Last Will and Testament is sent to SnifferBuddy.

The rest of the entries in `growbuddies_settings.json` are for other GrowBuddies.
## 3. Install the GrowBuddies Library
Open a terminal within the Python Virtual Environment.
```
pip install growbuddies
```
## 4. Run the Store Readings Script

If you have a SnifferBuddy that is sending out MQTT messages and a Gus device that is running an MQTT broker and InfluxDB database,
you can access the command line of the Gus device and type the following command:
```bash
store_readings
```
This will start running the [main function](growbuddies.store_readings.main) in the `store_readings.py` file.

If you've left the `log_level` attribute in `growbuddies_settings.json`, You should start seeing log messages such as:
```
2023-06-14 13:07:51,735:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/mqtt_code.py:84  on_connect   ...Connected to broker **gus**.  The ClientID is xerfbiiidx.  The result code is 0
2023-06-14 13:07:51,849:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/store_readings.py:42  on_snifferbuddy_status   ...-> SnifferBuddy is: online
2023-06-14 13:07:55,651:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/snifferbuddyreadings_code.py:26  __init__   ...-> Initializing SnifferBuddy class.
2023-06-14 13:09:02,784:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/store_readings.py:30  on_snifferbuddy_readings   ...SnifferBuddy Readings after a conversion from msg.payload {'name': 'sunshine', 'version': 0.1, 'co2': 855, 'humidity': 43.0893, 'light': 'ON', 'temperature': 88.412, 'vpd': 2.11}
2023-06-14 13:09:07,560:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/influxdb_code.py:52  store_readings   ...successfully wrote data: **[{'measurement': 'SnifferBuddy_Readings', 'fields': {'name': 'sunshine', 'version': 0.1, 'co2': 855, 'humidity': 43.0893, 'light': 'ON', 'temperature': 88.412, 'vpd': 2.11}}]** to influxdb database **gus** table **SnifferBuddy_Readings**
2023-06-14 13:09:11,618:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/snifferbuddyreadings_code.py:26  __init__   ...-> Initializing SnifferBuddy class.
2023-06-14 13:09:15,928:\[\]/home/pi/GrowBuddies/growbuddiesproject/growbuddies/store_readings.py:30  on_snifferbuddy_readings   ...SnifferBuddy Readings after a conversion from msg.payload {'name': 'sunshine', 'version': 0.1, 'co2': 854, 'humidity': 43.1198, 'light': 'ON', 'temperature': 88.34, 'vpd': 2.11}
```
## 5. Run as a SystemD Service
TBD
(_store_readings_code)=
## 6. Store_readings Code Walkthrough
```{eval-rst}
.. autofunction:: growbuddies.store_readings.main
.. autofunction:: growbuddies.store_readings.store_readings
```