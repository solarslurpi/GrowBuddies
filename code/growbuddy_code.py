import json
import logging
import os
from threading import Thread
import paho.mqtt.client as mqtt
from logging_handler import LoggingHandler

from influxdb import InfluxDBClient
import random
import string
from util_code import get_SnifferBuddy_dict


class GrowBuddy(Thread):

    """The GrowBuddy class assumes the

    """

    def __init__(
        self,
        topic_key="mqtt_snifferbuddy_topic",
        values_callback=None,
        status_callback=None,
        db_table_name=None,
        settings_filename="growbuddy_settings.json",
        log_level=logging.DEBUG,
    ):

        # Initialize a Thread so that each instance has it's own mqtt session on loop_start().
        # Use a unique name made of 10 lowercase ascii characters.
        self.unique_name = "".join(
            random.choice(string.ascii_lowercase) for i in range(10)
        )
        Thread.__init__(self, name=self.unique_name)
        self.values_callback = values_callback
        self.status_callback = status_callback
        self.db_table_name = db_table_name

        # Remember the key in the settings dictionary for the mqtt topic.
        self.topic_key = topic_key

        # Set up logging.  LoggingHandler gives stack trace information.
        self.logger = LoggingHandler(log_level)
        self.logger.debug(
            f"-> Initializing GrowBuddy class for task {self.unique_name}"
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
            self.settings = self._read_settings(settings_filename)
            self.logger.debug(f"...Settings: {self.settings}")
        except Exception as e:
            self.logger.error(f"...Exiting due to Error: {e}")
            os._exit(1)
        # Get a connection to the influxdb database, if needed.
        # The database must exist on the "hostname" Server (which is most likely named "GrowBuddy").
        if self.db_table_name is not None:
            try:
                self.influx_client = InfluxDBClient(host=self.settings["hostname"], database=self.settings["influxdb"]["db_name"])
            except ValueError as e:
                self.logger.error(f"ERROR! Was not able to connect to Influxdb.  Error: {e}")

    def start(self, loop_forever=True):
        """Starts up an mqtt client on a unique thread.

        """
        try:
            self.mqtt_client = mqtt.Client(self.unique_name)
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            self.mqtt_client.connect(self.settings["hostname"])
            # At this point, mqtt drives the code.
            self.logger.debug("Done with initialization. Handing over to mqtt.")
            self.mqtt_client.loop_forever()

        except Exception as e:
            self.logger.error(
                f"...In the midst of mqtt traffic.  Exiting due to Error: {e}")
            os._exit(1)

    def _LWT_callback(self, client, userdata, msg):
        message = msg.payload.decode(encoding="UTF-8")
        self.logger.info(f"LWT received message...{message}")
        if self.status_callback:
            self.status_callback(message)

    def _on_connect(self, client, userdata, flags, rc):
        """mqtt client callback called lonce the code has connected with the broker.
        Now we can subscribe to readings based on the topic initially passed in. We also subscribe to mqtt's
        LWT messages coming from each Buddy and retained by the GrowBuddy Broker.  The LWT messages is how
        we can determine if a Buddy is Online or Offline.

        Args:
            client (paho mqtt client instance): We got here because the mqtt library found the broker we want to
                work with and has assigned a session to this client.

            userdata : Not used.

            flags : Not used.

            rc (int): return code from the mqtt library connecting with the broker.

        """
        self.logger.debug(f"-> Mqtt connection returned {rc}")
        client.subscribe(self.settings[self.topic_key])
        LWT_topic = self.settings[self.topic_key].rsplit('/', 1)[0] + "/LWT"
        client.subscribe(LWT_topic)
        # Set a callback to handle LWT
        client.message_callback_add(LWT_topic, self._LWT_callback)
        self.logger.info(f"-> Subscribed to -->{self.settings[self.topic_key]}<--")

    def _on_message(self, client, userdata, msg):
        """INTERNAL METHOD. Received a reading.

        Args:
            msg (str):The message is a JSON string... if sent by SnifferBuddy, it looks something like


        """
        message = msg.payload.decode(encoding="UTF-8")
        self.logger.info(f"mqtt received message...{message}")
        # Send the message contents as a dictionary back to the values_callback.
        try:
            dict = json.loads(message)
            if self.topic_key == "mqtt_snifferbuddy_topic":
                # Since this is a SnifferBuddy reading, put in a simple dictionary.
                snifferbuddy_dict = get_SnifferBuddy_dict(dict)
                self.values_callback(snifferbuddy_dict)
                # Write reading to database table if desired.
            if self.db_table_name:
                self.db_write(snifferbuddy_dict)
            # TBD about this.  So far, the sensor is SnifferBuddy and everyone parties on that.  But one could imagine different
            # sensors.  Perhaps for water level or PAR value, etc.
            else:
                self.values_callback(dict)
        except Exception as e:
            self.logger.error(f"ERROR! Could not read the  measurement. ERROR: {e}")

        return

    def _on_disconnect(self, client, userdaata, rc=0):
        self.logger.debug("Disconnected result code {rc}")
        self.mqtt_client.loop_stop()

    def _read_settings(self, settings_filename) -> dict:
        """Opens the JSON file identified in settings_file and reads in the settings as a dict.

        Raises:
            Exception: When it can't find the file named by the settings_filename attribute.

        Returns:
            dict: including values for the mqtt broker, topic, and vpd setpoints at the different
            growth stages.

        """
        self.logger.debug(f"-> Reading in settings from {settings_filename} file.")
        dict_of_settings = {}
        try:
            with open(settings_filename) as json_file:
                dict_of_settings = json.load(json_file)
        except Exception as e:
            raise Exception(
                f"Could not open the settings file named {settings_filename}.  Error: {e}"
            )
        return dict_of_settings

    def db_write(self, dict) -> None:
        """write reading to the InfluxDB table (which is refered to as a measurement)

        Args:
            dict (dict): Dictionary of values that needs to be converted into a JSON foratted body.
            An example is given in the `InfluxDBClient documentation
            <https://influxdb-python.readthedocs.io/en/latest/include-readme.html#examples`_.


        There typically aren't any tags.  However, the fields will change bases on what sensor data there is to store.

        """
        try:
            if self.db_table_name == self.settings["influxdb"]["snifferbuddy_table_name"]:
                influxdb_data = [{"measurement": self.db_table_name,
                                  "fields": dict
                                  }
                                 ]
                # influxdb_dict.update(dict)
            self.influx_client.write_points(influxdb_data)
            self.logger.debug("Successfully added the reading to Influxdb.")
        except Exception as e:
            self.logger.error(
                f"ERROR! Was not able to add the data to Influxdb. ERROR: {e}"
            )
