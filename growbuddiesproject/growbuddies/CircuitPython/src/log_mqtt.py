from adafruit_logging import Handler, NOTSET


class MqttHandler(Handler):
    def __init__(self, mqtt_client, mqtt_topic, level: int = NOTSET):
        super().__init__(level)  # This calls the __init__() method of the Handler class
        self._mqtt_client = mqtt_client
        self._mqtt_topic = mqtt_topic

    def format(self, record):
        """Generate a string to log.

        :param record: The record (message object) to be logged
        """
        return super().format(record) + "\r\n"

    def emit(self, record):
        """Generate the message and write it to the UART.

        :param record: The record (message object) to be logged
        """
        # print(f"In emit.  record: {record}")
        self._mqtt_client.publish(self._mqtt_topic, self.format(record))
