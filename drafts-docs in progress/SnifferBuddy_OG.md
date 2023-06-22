(snifferbuddy_storereadings)=
## Store Readings {material-outlined}`storage;1em;sd-text-success`
```{button-link} https://github.com/solarslurpi/GrowBuddies/discussions
:outline:
:color: success

 {octicon}`comment;1em;sd-text-success` Comments & Questions
```

The `store-readings` script highlights the capabilities of the interactions between SnifferBuddy and [Gus](gus).

The script:

- Returns SnifferBuddy readings **including** vpd.
- Stores SnifferBuddy readings into an influxdb table within the database.
- Keeps the code aware of SnifferBuddy's status.
- Shows [Gus](gus)'s logging capability.

```{attention}
Before running the `store-readings` script:
1. There must be a working SnifferBuddy and Gus.
2. The steps below must be completed.
```

```{button-link} https://github.com/solarslurpi/GrowBuddies/blob/930420abc7ddd4cf4c74c408d61819eec0968a44/growbuddies-project/growbuddies/examples/snifferbuddy_storereadings.py
:outline:
:color: success

 {octicon}`mark-github;1em;sd-text-success` View Code
```

### 1. Get into a Python Virtual Environment
A Python virtual environment with the growbuddies package installed must exist before running the Python script.  We'll run the script on Gus (the Raspberry Pi Server).
- Get to a command line prompt on Gus.
- Create a folder where the script will be run, e.g.:
```
$mkdir growbuddies
```
- Change into this directory, e.g.:
```
$cd growbuddies
```
- Make sure you have Python3 on Gus. e.g.:
```
$ python3 --version
Python 3.9.2
```
- Create a Python Virtual Environment using the venv Python module.  e.g.:
```
python3 -m venv .venv
```
- Activate the Virtual Environment.  e.g.:
```
$ source .venv/bin/activate
(.venv) pi@gus:~/test$

(.venv) pi@gus:~/test$ python --version
Python 3.9.2
```
The prompt is a visual clue we are now within the Virtual Environment.
### 2. Install the GrowBuddies package
```
(.venv) pi@gus:~/test$ pip install GrowBuddies --upgrade
```
```{note}
Including the `--upgrade` option will upgrade the GrowBuddies package to the latest version.  This will matter when running the script.
```
### 3. Run the Script
```
(.venv) pi@gus:~/test$ store-readings
```
You should start seeing a lot of logging lines.  These give you a great idea what is going on in the code.  If you are able to store readings into influxdb,
```{literalinclude} store-readings.txt
:language: bash
```

```{eval-rst}
.. automodule:: growbuddies.store_readings
   :members:
```

## About Logging {material-outlined}`description;1em;sd-text-success`

```{button-link} https://github.com/solarslurpi/GrowBuddies/blob/5942d40bff58e11be8e78d7296eb0daa9fff5a17/code/logginghandler.py
:outline:
:color: success

 {octicon}`mark-github;1em;sd-text-success` View Code
```
```{eval-rst}
.. automodule:: growbuddies.logginghandler
   :members:
```

## Plot Readings  {material-outlined}`multiline_chart;1em;sd-text-success`
```{note}
These steps assume you have already [installed Grafana on Gus](make_gus) and kept the defaults (database, hostname) to `gus`.
```

The data collected while running a Python Script - like the code discussed under the  {ref}`snifferbuddy_storereadings` topic - can be viewed within the powerful
[Grafana](https://en.wikipedia.org/wiki/Grafana) graphing package.

### Login to Grafana

```{note}
You must install Grafana on Gus() first.  For this step, see the [Make Gus()](make_gus) step.
```
[The pimylifeup web post](https://pimylifeup.com/raspberry-pi-grafana/) does an excellent job walking us through setting up Grafana login.

**Start at step 2**. You'll see the line `http://<IPADDRESS>:3000`.  Most likely you will use the URL `http://gus:3000`.

- log in to Grafana (go through steps 2 through 5)

As pimylifeup notes: _At this point, you should now have Grafana up and running on your Raspberry Pi and now be able to access its web interface._
```
http://gus:3000
```
### Connect to the Gus Database
```{note}
These steps assume you kept the defaults (database, hostname) to `gus`.
```
Now that we can log into Grafana, let's connect to the gus database.

#### Choose the Data Source

From the Grafana screen, choose to add a data source.
:::{figure} images/grafana_add_datasource.jpg
:align: center
:scale: 100

Grafana Data Source Options
:::

You'll be greeted by a list of several data source choices.  Choose `influxDB`.
#### Name the Data Source
Name the database `Gus` and toggle the Default switch to the ON position.
:::{figure} images/grafana_influxdb_data_source_name.jpg
:align: center
:scale: 100

Grafana - InfluxDB Name the Data Source
:::
#### Fill in HTTP Connection Parameters
Fill in the URL, choose Basic Auth, then provide the Basic Auth password to `gus`.

:::{figure} images/grafana_influxdb_http_config.jpg
:align: center
:scale: 50

Grafana - InfluxDB HTTP Connection Settings
:::
#### Fill in influxDB Parameters
Now fill in the influxDB parameters.

:::{figure} images/grafana_influxdb_influxdb_config.jpg
:align: center
:scale: 75

Grafana - InfluxDB InfluxDB Settings
:::
Choose Save & Test ...and...
_**Hopefully**_ you can smile looking at:
:::{figure} images/grafana_influxdb_data_test_worked.jpg
:align: center
:scale: 75

Grafana - InfluxDB Connection Success
:::
### Plot Readings
Grafana's workflow to get to looking at sensor readings includes:
#### Create a Dashboard
:::{figure} images/grafana_new_dashboard.jpg
:align: center
:scale: 75

Grafana - Create a New Dashboard
:::
#### View Readings
Create a dashboard then create a panel within the dashboard.

Now you are at what Grafana calls a Panel.  The image shows a panel set up to show vpd `SnifferBuddyReadings()`.
1. Set the Data Source to Gus.
2. Set the Table (InfluxDB calls a table a Measurement), which is the `From` field. is set to "sniff2" (recall this is the table created after running the {ref}`snifferbuddy_storereadings`.
3. Set the `Select` field to `vpd`.
4. The time was to a range that includes `SnifferBuddyReadings()`.
After setting the parameters similar to what is done in the image, you should see a plot similar to the one in the image.  There are a few differences based on configuring Grafana plot features.  They are all covered in the online Grafana documentation.

:::{figure} images/grafana_snifferbuddyreadings_vpd.jpg
:align: center
:scale: 75
A plot of SnifferBuddyReadings for vpd
:::

The results point to an average vpd at that date/time range of about 1.3.
### Analyze Readings
Looking at [FLU's VPD Chart](https://www.canr.msu.edu/floriculture/uploads/files/Water%20VPD.pdf)
:::{figure} images/vpd_chart.jpg
:align: center
:scale: 75

FLU's VPD Chart
:::

```{danger}
A vpd reading of 1.3 is saying the grow environment is stressful for the plant.
```
The humidity or the temperature could be adjusted.  Here is a plot of the temperature and vpd.  While the vpd averages about 1.3, the temperature ranges between 73 and 75.  This is because my grow tent environment is in my house, which is climate controlled.  The LED lights raise the temperature a bit.  The fans cool the temperature a bit.  It's pretty ideal.  Thus, [MistBuddy](mistbuddy_doc) focuses on turning a humidifier on and off for just the right amount of time.

:::{figure} images/grafana_snifferbuddyreadings_vpd._and_temp.jpg
:align: center
:scale: 65

A plot of SnifferBuddyReadings for vpd and temperature.
:::


## Run as a Service
Running {ref}`snifferbuddy_storereadings` over ssh will stop when the desktop gets connected.  What needs to happen is to set up {ref}`snifferbuddy_storereadings` as a [Systemd service](systemd_doc).

