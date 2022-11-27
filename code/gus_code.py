#
# Gus does the heavy lifting for the GrowBuddies.
#
# Copyright 2022 Margaret Johnson

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
import json
import logging
from logginghandler import LoggingHandler
import os
from threading import Thread
import paho.mqtt.client as mqtt


from influxdb import InfluxDBClient
import random
import string
from snifferbuddyreadings_code import snifferBuddyReadings

snifferbuddy_topic = "snifferbuddy_topic"
settings_filename = "growbuddies_settings.json"


class Gus(Thread):

    """The Gus class provides:

    * Callbacks for receiving sensor readings.  Under the covers, mqtt messaging is managed.

    * A way to publish mqtt messages to Buddies (e.g.: to turn a plug on and off during testing).

    * Method to write readings to an InfluxDB measurement (which is what Influx seems to call a Table within a database).

    * Rich logging for debugging and auditing.

    Args:
        topic_key (str, optional): The dictionary key for the full topic in the settings file.  In mqtt, the topic key is given
        to the Publish/Subscribe methods.  Defaults to `snifferbuddy_topic`.

        SnifferBuddyReadings_callback (function, optional): Function called by Gus to return an instance of a SnifferBuddyReadings().

        status_callback (function, optional): Function called by Gus when an LWT message is received. The `status_callback` function receives
        a string containing either `online` or `offline`.

        SnifferBuddyReadings_table_name (str, optional): Name of measurement table in influxdb that stores snifferBuddy readings.  Defaults to None.

        settings_filename (str, optional): All the settings used by Gus. Defaults to "gus_settings.json".

        log_level (constant, optional): Defined by Python's logging library. Defaults to logging.DEBUG.

    """
    def __init__(
        self,
        subscribe_to_sensor=True,
        topic_key=snifferbuddy_topic,  # Many times the caller will want to get snifferBuddy readings.
        msg_value=None,  # Used when publishing a message.
        SnifferBuddyReadings_callback=None,
        status_callback=None,
        SnifferBuddyReadings_table_name=None,  # Provide a table name to use in influxdb to store the readings.
        settings_filename=settings_filename,
        log_level=logging.DEBUG,
    ):

        # Initialize a Thread so that each instance has it's own mqtt session on loop_start().
        # Use a unique name made of 10 lowercase ascii characters.
        self.unique_name = "".join(
            random.choice(string.ascii_lowercase) for i in range(10)
        )
        Thread.__init__(self, name=self.unique_name)
        self.SnifferBuddyReadings_callback = SnifferBuddyReadings_callback
        self.status_callback = status_callback
        self.SnifferBuddyReadings_table_name = SnifferBuddyReadings_table_name

        # Remember the key in the settings dictionary for the mqtt topic.
        self.topic_key = topic_key
        self.settings_filename = settings_filename
        self.subscribe_to_sensor = subscribe_to_sensor
        self.msg_value = msg_value

        # Set up logging.  LoggingHandler gives stack trace information.
        self.logger = LoggingHandler(log_level)
        self.logger.debug(
            f"-> Initializing Gus class for task {self.unique_name}"
        )
        # Set the working directory to where the Python files are located.
        self.logger.debug(
            f"--> Current Directory prior to setting to the file location is {os.getcwd()}"
        )
        cfd = os.path.dirname(os.path.realpath(__file__))
        os.chdir(cfd)
        self.logger.debug(f"--> Current Directory is {os.getcwd()}")

        # Get settings out of JSON file.
        try:
            self.settings = self.read_settings()
            self.logger.debug(f"...Settings: {self.settings}")
        except Exception as e:
            self.logger.error(f"...Exiting due to Error: {e}")
            os._exit(1)

        try:
            # Get a connection to the influxdb database.
            # The database must exist on the "hostname" Server (which is most likely named "Gus").
            self.influx_client = InfluxDBClient(host=self.settings["hostname"])
            # Create the database - according to influxdb docs, if the database is already created
            # nothing happens.  But if the database doesn't exist, we'll fail.  So each time try
            # to create for the few times when it doesn't exist.
            db_name = self.settings["influxdb"]["db_name"]
            self.influx_client.create_database(db_name)
            # Set the client to use this database.
            self.influx_client.switch_database(db_name)
        except ValueError as e:
            self.logger.error(f"ERROR! Was not able to connect to Influxdb.  Error: {e}")

    def start(self):
        """Starts up an mqtt client on a unique thread.

        """
        try:
            self.mqtt_client = mqtt.Client(self.unique_name)
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            self.mqtt_client.on_publish = self._on_publish
            self.mqtt_client.connect(self.settings["hostname"])
            # At this point, mqtt drives the code.
            self.logger.debug("Done with initialization. Handing over to mqtt.")
            self.mqtt_client.loop_forever()

        except Exception as e:
            self.logger.error(
                f"...In the midst of mqtt traffic.  Exiting due to Error: {e}")
            os._exit(1)

    @property
    def settings_dict(self):
        return self.settings

    def _LWT_callback(self, client, userdata, msg):
        """mqtt callback we set up earlier to be called when a Last Will and Testament (LWT) message
        is available.  Tasmota's LWT messages are either "Online" or "Offline".

        Args:
            client (paho mqtt client instance): Opaque blob passed about identifying the mqtt session.
            userdata : Not used.
            msg (str): The Last Will and Testament strings from a Tasmota device is either
                "Online" or "Offline".
        """
        message = msg.payload.decode(encoding="UTF-8")
        self.logger.info(f"LWT received message...{message}")
        if self.status_callback:
            self.status_callback(message)

    def _on_connect(self, client, userdata, flags, rc):
        """mqtt client callback called once the code has connected with the broker.
        Now we can subscribe to readings based on the topic initially passed in. We also subscribe to mqtt's
        LWT messages coming from each Buddy and retained by the Gus Broker.  The LWT messages is how
        we can determine if a Buddy is Online or Offline.

        Args:
            client (paho mqtt client instance): We got here because the mqtt library found the broker we want to
                work with and has assigned a session to this client.

            userdata : Not used.

            flags : Not used.

            rc (int): return code from the mqtt library connecting with the broker.

        """
        self.logger.debug(f"-> Mqtt connection returned {rc}")
        mqtt_topic = self.settings["mqtt"][self.topic_key]
        if not self.subscribe_to_sensor:
            self.mqtt_client.publish(mqtt_topic, self.msg_value)
            return
        if self.subscribe_to_sensor:
            client.subscribe(mqtt_topic)
            self.logger.info(f"-> Subscribed to -->{self.topic_key}<--")
        LWT_topic = mqtt_topic.rsplit('/', 1)[0] + "/LWT"
        client.subscribe(LWT_topic)
        # Set a callback to handle LWT
        client.message_callback_add(LWT_topic, self._LWT_callback)

    def _on_message(self, client, userdata, msg):
        """Received a message for the client.subscribe() we subscribed to in _on_connect().

        Args:
            client (paho mqtt client instance): Opaque blob passed about identifying the mqtt session.

            userdata : Not used.

            msg (str):The message is a JSON string... if sent by SnifferBuddy, it looks something like
        """
        message = msg.payload.decode(encoding="UTF-8")
        self.logger.info(f"mqtt received message...{message}")
        # Send the message contents as a dictionary back to the values_callback.
        try:
            mqtt_dict = json.loads(message)
            s = snifferBuddyReadings(mqtt_dict)
            if self.SnifferBuddyReadings_callback:
                self.SnifferBuddyReadings_callback(s)
            # Write reading to database table if desired.
            if self.SnifferBuddyReadings_table_name:
                try:
                    self.db_write(self.SnifferBuddyReadings_table_name, s.dict)
                except Exception as e:
                    self.logger.error(f"ERROR! Could not write the snifferBuddy Values.  error: {e}")
        except Exception as e:
            self.logger.error(f"ERROR! {e}")

        return

    def _on_publish(self, client, userdata, msg_id):
        self.logger.debug(f"message ID {msg_id} was published.")
        # If the caller hasn't subscribed to anything, exit the app.
        if not self.subscribe_to_sensor:
            exit(0)

    def _on_disconnect(self, client, userdata, rc):
        self.logger.debug(f"Disconnected result code {rc}")
        self.mqtt_client.loop_stop()

    def read_settings(self) -> dict:
        """Opens the JSON file identified in settings_file and reads in the settings as a dict.

        Raises:
            Exception: When it can't find the file named by the settings_filename attribute.

        Returns:
            dict: A dictionary of values for things like the name of the mqtt broker, mqtt topics,
            vpd setpoints, etc.  The file provided is named "gus_settings.json".

        """
        self.logger.debug(f"-> Reading in settings from {self.settings_filename} file.")
        dict_of_settings = {}
        try:
            with open(self.settings_filename) as json_file:
                dict_of_settings = json.load(json_file)
        except Exception as e:
            raise Exception(
                f"Could not open the settings file named {self.settings_filename}.  Error: {e}"
            )
        return dict_of_settings

    def db_write(self, table_name, dict) -> None:
        """Write reading to the InfluxDB table (which is refered to as a measurement).

        Args:
            dict (dict): The fields value passed to the influx client.
                An example is given in the

                `InfluxDBClient documentation <https://influxdb-python.readthedocs.io/en/latest/include-readme.html#examples>`_

        """
        # TODO: Other context specific writes to tables...
        try:
            influxdb_data = [{"measurement": table_name,
                              "fields": dict
                              }
                             ]
            self.influx_client.write_points(influxdb_data)
            self.logger.debug(f"Successfully added the reading to Influxdb table {table_name}.")
        except Exception as e:
            self.logger.error(
                f"ERROR! Was not able to add the data to Influxdb. ERROR: {e}"
            )
