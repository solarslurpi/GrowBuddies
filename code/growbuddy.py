import json
import logging
import os
from threading import Thread  # Necessary so that each sensor has it's own mqtt thread.
import paho.mqtt.client as mqtt
from logging_handler import LoggingHandler
from influxdb import InfluxDBClient


#TODO TTL Checking.  I did this in node red.


class GrowBuddy(Thread):
    """The GrowBuddy Parent Class and children classes run on a Raspberry Pi as the GrowBuddy Service.
    Children classes of the GrowBuddy class inherit:
        * logging for debugging and auditing.
        * handling of `mqtt <https://mqtt.org/>`_ messages.
        * writing readings to an InfluxDB measurement (which is what Influx seems to call a Table within a database).


    Args:
        task (str): _description_
        values_callback (_type_, optional): _description_. Defaults to None.
        settings_filename (str, optional): _description_. Defaults to 'growbuddy_settings.json'.
        log_level (_type_, optional): _description_. Defaults to logging.DEBUG.

    """
    def __init__(self,task:str,values_callback=None,settings_filename='growbuddy_settings.json',log_level=logging.DEBUG):
        """_summary_

        Args:
            task (str): _description_
            values_callback (_type_, optional): _description_. Defaults to None.
            settings_filename (str, optional): _description_. Defaults to 'growbuddy_settings.json'.
            log_level (_type_, optional): _description_. Defaults to logging.DEBUG.
        """

        # Initialize a Thread so that each instance has it's own mqtt session on loop_start().
        Thread.__init__(self,name=task)
        self.task = task
        self.values_callback = values_callback

        
        # Set up logging.  LoggingHandler gives stack trace information.
        self.logger = LoggingHandler(log_level)
        self.logger.debug(f"-> Initializing GrowBuddy class for task {self.task}")
        # Set the working directory to where the Python files are located.
        self.logger.debug(f'--> Current Directory prior to setting to the file location is {os.getcwd()}')
        cfd = os.path.dirname(os.path.realpath(__file__))
        os.chdir(cfd)
        self.logger.debug(f'--> Current Directory is {os.getcwd()}')

        # Get settings out of JSON file.
        try:
            self.settings = self._read_settings(settings_filename)
            self.logger.debug(f'...Settings: {self.settings}')
        except Exception as e:
            self.logger.error(f'...Exiting due to Error: {e}')
            os._exit(1)
        # Set up a connection to the grpwbuddy database that has already been created.
        try:
            self.influx_client = InfluxDBClient(host="growbuddy", database="growbuddy")
        except ValueError as e:
           self.logger.error(f'ERROR! Was not able to connect to the Influxdb.  Error: {e}')
        # Connect up with mqtt.
        try:
            self.mqtt_client = mqtt.Client(self.settings[self.task])
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            self.mqtt_client.connect(self.settings['mqtt_broker'])
            # At this point, mqtt drives the code.
            self.logger.debug(f'Done with initialization. Handing over to mqtt.')
            self.mqtt_client.loop_start()


        except Exception as e:
            self.logger.error(f'...In the midst of mqtt traffic.  Exiting due to Error: {e}')
            os._exit(1)

    def _on_connect(self,client, userdata, flags, rc):
        """Called back by the mqtt library once the code has connected with the broker.  Now we can subscribe to soil moisture readings.

        Args:
            client (opaque structure passed along through the mqtt library. It maintains the mqtt client connection to the broker): We got here because the mqtt library found the broker we want to work with and has assigned our
            session to this client.
            userdata (_type_): Not used.
            flags (_type_): Not used.
            rc (int): return code from the mqtt library connecting with the broker.
        """
        self.logger.debug(f"-> Mqtt connection returned {rc}")
        client.subscribe(self.settings[self.task])
        self.logger.info(f'-> Subscribed to {self.settings[self.task]}')


    def _on_message(self, client, userdata, msg) :
        """Received a `tele/soil_moisture/SENSOR` msg (sensor reading) from the soil moisture sensor (obtained through the growbuddy broker).  

        Args:
            userdata (_type_): Not used.
            msg (str):The message is something like
            {"Time":"2022-09-23T09:43:49","ANALOG":{"A0":823}}
            it is sent by the soil moisture sensor every twenty seconds.
        """
        message = msg.payload.decode(encoding='UTF-8')
        self.logger.info(f'mqtt received message...{message}')
     
        try:
            dict = json.loads(message)
            self.values_callback(dict)
        except Exception as e:
            self.logger.error(f'ERROR! Could not read the  measurement. ERROR: {e}')
        return

    def _on_disconnect(self, client, userdaata, rc=0):
        self.logger.debug("Disconnected result code {rc}")
        self.mqtt_client.loop_stop()

    def _read_settings(self,settings_filename) -> dict:
        """Opens the JSON file identified in settings_file and reads in the settings as a dict.

        Raises:
            Exception: When it can't find the file named by the settings_filename attribute. 
        Returns:
            dict: including values for the mqtt broker, topic, and vpd setpoints at the different 
            growth stages.
        """
        self.logger.debug(f'-> Reading in settings from {settings_filename} file.')
        dict_of_settings = {}
        try:
            with open(settings_filename) as json_file:
                dict_of_settings = json.load(json_file)
        except Exception as e:
            raise Exception(f'Could not open the settings file named {settings_filename}')
        return dict_of_settings

    def db_write(self,data) -> None:
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
            self.logger.debug(f'Successfully added the reading to Influxdb.')
        except Exception as e:
            self.logger.error(f'ERROR! Was not able to add the data to Influxdb. ERROR: {e}')

