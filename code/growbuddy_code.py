import json
import logging
import os
from threading import Thread  # Necessary so that each sensor has it's own mqtt thread.
import paho.mqtt.client as mqtt
from logging_handler import LoggingHandler

# from influxdb import InfluxDBClient
import random
import string

# TODO TTL Checking.  I did this in node red.


class GrowBuddy(Thread):
    """The GrowBuddy Parent Class and children classes run on a Raspberry Pi as the GrowBuddy Service.
    Children classes of the GrowBuddy class inherit:
        * logging for debugging and auditing.
        * handling of `mqtt <https://mqtt.org/>`_ messages.
        * writing readings to an InfluxDB measurement (which is what Influx seems to call a Table within a database).


    Args:
        topic_key (str, optional): The dictionary key for the full topic in the settings file.
        Defaults to "mqtt_snifferbuddy_topic".
        Which means by default, GrowBuddy will receive messages from SnifferBuddy.  The messages from SnifferBuddy contain
        the readings for air temp, relative humidity, CO2, and light level.
        values_callback (function, optional): Function called by GrowBuddy to return messages received by the mqtt topic.
        Defaults to None.
        status_callback (function optional): Will be called if GrowBuddy detects a problem accessing the Buddy.
        settings_filename (str, optional): All the settings used by the GrowBuddy system. Defaults to "growbuddy_settings.json".
        log_level (constant, optional): Defined by Python's logging library. Defaults to logging.DEBUG.
    """

    def __init__(
        self,
        topic_key="mqtt_snifferbuddy_topic",
        values_callback=None,
        status_callback=None,
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

    def start(self, loop_forever=True):
        """Starts up an mqtt client on a unique thread.
        """
        # # Set up a connection to the growbuddy database that has already been created.
        # try:
        #     self.influx_client = InfluxDBClient(host="growbuddy", database="growbuddy")
        # except ValueError as e:
        #     self.logger.error(
        #         f"ERROR! Was not able to connect to the Influxdb.  Error: {e}"
        #     )
        # Connect up with mqtt.
        try:
            self.mqtt_client = mqtt.Client(self.unique_name)
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            self.mqtt_client.connect(self.settings["mqtt_broker"])
            # At this point, mqtt drives the code.
            self.logger.debug("Done with initialization. Handing over to mqtt.")
            self.mqtt_client.loop_forever() 

        except Exception as e:
            self.logger.error(
                f"...In the midst of mqtt traffic.  Exiting due to Error: {e}")
            os._exit(1)
    
    def _on_connect(self, client, userdata, flags, rc):
        """INTERNAL METHOD.  Called back by the mqtt library once the code has connected with the broker.
        Now we can subscribe to readings based on the topic initially passed in. We also subscribe to mqtt's
        LWT messages coming from each Buddy and retained by the GrowBuddy Broker.

        Args:
            client (opaque structure passed along through the mqtt library. It maintains the mqtt client connection to
            the broker): We got here because the mqtt library found the broker we want to work with and has assigned a
            session to this client.
            userdata (_type_): Not used.
            flags (_type_): Not used.
            rc (int): return code from the mqtt library connecting with the broker.
        """
        self.logger.debug(f"-> Mqtt connection returned {rc}")
        client.subscribe(self.settings[self.topic_key])
        LWT_topic = self.settings[self.topic_key].rsplit('/', 1)[0] + "/LWT"
        client.subscribe(LWT_topic)
        self.logger.info(f"-> Subscribed to -->{self.settings[self.topic_key]}<--")

    def _on_message(self, client, userdata, msg):
        """INTERNAL METHOD. Received a `tele/snifferbuddy/SENSOR` msg (sensor reading) from SnifferBuddy (obtained
        through the growbuddy broker).  Next, a new value for the VPD is calculated and the values are sent to the
        caller if a callback function was provided.

        Args:
            msg (str):The message is a JSON string sent by SnifferBuddy that looks something like
                {"Time":"2022-09-06T08:52:59",
                "ANALOG":{"A0":542},
                "SCD30":{"CarbonDioxide":814,"eCO2":787,"Temperature":71.8,"Humidity":61.6,"DewPoint":57.9},"TempUnit":"F"}

        """
        message = msg.payload.decode(encoding="UTF-8")
        self.logger.info(f"mqtt received message...{message}")

        try:
            dict = json.loads(message)
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

    def db_write(self, data) -> None:
        r"""write the sensor reading to the InfluxDB table (which is refered to as a measurement).

        Args:
            data (JSON): The format is something like:

        .. code-block:: python

                measurement = "sensor_data"
                data = [
                    {
                    "measurement": measurement,
                    "tags": {
                        "location": location,
                        },
                    "fields": {
                        "temperature" : temperature,
                        "humidity": humidity
                        }
                    }
                ]

        There typically aren't any tags.  However, the fields will change bases on what sensor data there is to store.
        """
        try:
            self.influx_client.write_points(data)
            self.logger.debug("Successfully added the reading to Influxdb.")
        except Exception as e:
            self.logger.error(
                f"ERROR! Was not able to add the data to Influxdb. ERROR: {e}"
            )
