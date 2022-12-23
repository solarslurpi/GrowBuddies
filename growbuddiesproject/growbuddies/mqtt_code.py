import paho.mqtt.client as mqtt
import threading
import random
import string


class MQTTClient:
    """A class that represents an MQTT client.

    This class uses the `paho-mqtt` library to connect to an MQTT broker and
    subscribe to specified topics. It also provides methods for handling
    incoming messages and performing cleanup when the client is stopped.

    Attributes:
        client_id (str): The client ID is a string that uniquely identifies the client to the MQTT broker.
        It is used by the broker to identify the client and manage its connection. If a client ID is not provided,
        a unique random client ID will be generated to use instead.
        host (str): The hostname or IP address of the MQTT broker.
        topics_and_callbacks (dict): A dictionary mapping MQTT topics to callback functions.
        client (paho.mqtt.client.Client): The MQTT client object.

    Methods:
        on_connect(client, userdata, flags, rc): A callback function that is called when the client
            connects to the MQTT broker.
        on_disconnect(client, userdata, rc): A callback function that is called when the client
            disconnects from the MQTT broker.
        on_message(client, userdata, msg): A callback function that is called when the client
            receives a message from the MQTT broker.
        start(): Connects to the MQTT broker and starts the client's message loop.
        stop(): Stops the client's message loop and disconnects from the MQTT broker.
    """

    def __init__(self, client_id=None, host="gus", callbacks_dict=None):
        # The client ID is a unique identifier that is used by the broker to identify this
        # client. If a client ID is not provided, a unique ID is generated and used instead.
        if not client_id:
            client_id = "".join(random.choice(string.ascii_lowercase) for i in range(10))
        self.client_id = client_id
        self.host = host
        self.callbacks_dict = callbacks_dict or {}
        try:
            self.client = mqtt.Client(client_id=self.client_id, clean_session=False)
        except Exception as e:
            print(f"{e}")  # TODO: Logging.
        # This will be sent to subscribers who asked to receive the LWT for this mqtt client.
        self.client.will_set("/lwt", "offline", qos=1, retain=False)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribe to the topics passed in the topics_and_callbacks_dict.
        for k in self.callbacks_dict:
            self.client.subscribe(k)

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.")

    def on_message(self, client, userdata, msg):
        # print("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))
        try:
            for k in self.callbacks_dict:
                if k == msg.topic:
                    self.callbacks_dict[k](msg.payload.decode("utf-8"))

        except KeyError as e:
            print(f"{e}")

    def start(self):
        self.client.connect(self.host)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()


class MQTTService:
    """This class wraps an `MQTTClient` object and runs it in a separate thread. It provides methods for starting
    and stopping the service. This wrapper is necessary because a systemd service requires a blocking call, such as
    loop_forever(), to run indefinitely in the background. Since the loop_forever() method blocks the thread it is
    called in, running the MQTTClient in a separate thread allows the service to run in the background without blocking
    the main thread.

    Attributes:
        client (MQTTClient): The MQTT client object.
        thread (threading.Thread): The thread that the MQTT client runs in.

    Methods:
        start(): Starts the MQTT client in a separate thread.
        stop(): Stops the MQTT client and waits for the thread to join.

    ```{note} The default mqtt broker is Gus
    ```

    """

    def __init__(self, client_id="mqttservice_clientid", host="gus", callbacks_dict=None):
        # topics_and_callback_json has the callback functions as strings.  These need to be converted.

        self.client = MQTTClient(client_id, host, callbacks_dict)
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.client.start)
        self.thread.start()

    def stop(self):
        self.client.stop()
        self.thread.join()
