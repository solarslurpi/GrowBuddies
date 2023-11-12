"""Test
:py:meth:`growbuddies.mqtt_code.MQTTClient.on_connect`

"""
import paho.mqtt.client as mqtt
import threading
import random
import string
from settings_code import Settings
from logginghandler import LoggingHandler

#

# MQTT Error values from https://github.dev/eclipse/paho.mqtt.python/tree/master/src/paho/mqtt/client.py
rc_codes = {
    "MQTT_ERR_AGAIN": -1,
    "MQTT_ERR_SUCCESS": 0,
    "MQTT_ERR_NOMEM": 1,
    "MQTT_ERR_PROTOCOL": 2,
    "MQTT_ERR_INVAL": 3,
    "MQTT_ERR_NO_CONN": 4,
    "MQTT_ERR_CONN_REFUSED": 5,
    "MQTT_ERR_NOT_FOUND": 6,
    "MQTT_ERR_CONN_LOST": 7,
    "MQTT_ERR_TLS": 8,
    "MQTT_ERR_PAYLOAD_SIZE": 9,
    "MQTT_ERR_NOT_SUPPORTED": 10,
    "MQTT_ERR_AUTH": 11,
    "MQTT_ERR_ACL_DENIED": 12,
    "MQTT_ERR_UNKNOWN": 13,
    "MQTT_ERR_ERRNO": 14,
    "MQTT_ERR_QUEUE_SIZE": 15,
    "MQTT_ERR_KEEPALIVE": 16,
}


def get_hostname():
    settings = Settings()
    settings.load()
    return settings.get("hostname")


class MQTTClient:
    """A more optimized way to publish and subscribe to the Gus MQTT broker.

    If the calling code logic is subscribing to MQTT topics, then access to the
    MQTTClient() must go through MQTTService().

    If the calling code logic is strictly publishing MQTT messages, then access
    to publishing mqtt messages can all be done through MQTTClient().

    It also provides methods for handling incoming messages and performing cleanup
    when the client is stopped.

    Attributes:
        host (str): The hostname or IP address of the MQTT broker.

        callbacks_dict (dict): A dictionary mapping MQTT topics to callback functions.

    """

    def __init__(self, callbacks_dict=None):
        self.logger = LoggingHandler()
        # The client ID is a unique identifier that is used by the broker to identify this
        # client. If a client ID is not provided, a unique ID is generated and used instead.

        self.client_id = "".join(
            random.choice(string.ascii_lowercase) for i in range(10)
        )
        self.host = get_hostname()
        self.callbacks_dict = callbacks_dict or {}
        try:
            self.client = mqtt.Client(client_id=self.client_id, clean_session=False)
        except Exception as e:
            self.logger.debug(f"Error creating MQTT client.  The error is {e}.")
        # This will be sent to subscribers who asked to receive the LWT for this mqtt client.
        self.client.will_set("/lwt", "offline", qos=1, retain=False)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc) -> int:
        """Callback function that is called when the client connects to the MQTT broker."""
        self.logger.debug(
            f"Connected to broker **{self.host}**.  The ClientID is {self.client_id}.  The result code is {str(rc)}"
        )
        if rc != 0:
            self.logger.error(
                f"Received an unexpected error in on_connect.  The error is {rc_codes[rc]}"
            )
            return rc
        # Subscribe to the topics passed in the topics_and_callbacks_dict.
        # for k in self.callbacks_dict:
        #     self.client.subscribe(k)
        # return rc

    def on_disconnect(self, client, userdata, rc) -> int:
        if rc != 0:
            self.logger.error(
                f"Received an unexpected disconnect.  The error is {rc_codes[rc]}"
            )
        return rc

    def on_message(self, client, userdata, msg) -> None:
        """Callback function that is called when the client receives a message from the MQTT broker.

        Args:
            msg (str): An MQTT message.

        To determine which callback function to call for a specific MQTT message topic, a callbacks_dict is used
        to map the topic to the appropriate callback function. The callbacks_dict is passed in by the caller and
        is created using the :py:meth:`growbuddies.settings_code.Settings.get_callbacks` method. This allows
        for a generic way to handle different MQTT topics and their corresponding callback functions.

        The callbacks_dict is searched to find the function that should be executed when the topic of the incoming MQTT
        message matches a key in the dict.

        """
        self.logger.debug(f"Received MQTT message: {msg.payload.decode('utf-8')}")
        # try:
        #     for k in self.callbacks_dict:
        #         if k == msg.topic:
        #             self.callbacks_dict[k](msg.payload.decode("utf-8"))
        # except KeyError as e:
        #     self.logger.error(
        #         f"There was a KeyError when attempting to call one of the callback functions.  The error is {e}"
        #     )

    def publish(self, topic, message, qos=1):
        """Publishes an MQTT message to the MQTT broker.  The MistBuddy method :py:meth:`mistbuddy.mistbuddy_code.turn_on_mistBuddy`
        uses this method to publish MQTT messages to the MistBuddy topic."""
        rc = self.client.publish(topic, message, qos)
        return rc

    def disconnect(self):
        self.client.disconnect()

    def start(self):
        """Connects to the MQTT broker and starts the client's message loop.  Used with MQTTService()."""
        self.client.connect(self.host)
        self.client.loop_start()

    def stop(self):
        """Stops the client's message loop and disconnects from the MQTT broker. Used with MQTTService()."""
        self.client.loop_stop()
        self.client.disconnect()


class MQTTService:
    """GrowBuddies code that subscribes to topics and runs as a systemd service will need to get to the MQTT client through
    MQTTService(). This is necessary because a systemd service requires a blocking call, such as loop_forever(), in order
    to run continuously in the background. However, the loop_forever() method prevents the thread from continuing. By using
    a separate thread for the MQTTClient, the service can run in the background without blocking the main thread.


    Attributes:
        callbacks_dict (dict): A dictionary mapping MQTT topics to callback functions.  The callbacks_dict is created by
        calls to the :py:class:`growbuddies.settings_code.Settings` class.

    Methods:
        start(): Starts the MQTT client in a separate thread.

        stop(): Stops the MQTT client and waits for the thread to terminate.

    .. note::
       The default mqtt broker is Gus

    """

    def __init__(self, callbacks_dict=None):
        # topics_and_callback_json has the callback functions as strings.  These need to be converted.

        self.client = MQTTClient(callbacks_dict)
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.client.start)
        self.thread.start()

    def stop(self):
        self.client.stop()
        self.thread.join()
