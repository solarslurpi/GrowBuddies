import random
import pytest
import time
import sys

sys.path.append("../")
from growbuddies.mqtt_code import MQTTClient
from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings


class MqttPublish:
    def __init__(self, topics_messages_list=None):
        if topics_messages_list is None:
            raise ValueError("A topic_message_dict must be provided.")
        self.client = MQTTClient()
        self.client.start()
        self.logger = LoggingHandler()
        self.topics_messages_list = topics_messages_list




    # def test_publish_fixed_interval(self, topic, message):
    #     self.publish_messages(topic="test/topic", message="Hello world!", period=10, variable_timing=False, max_messages=5)
    # Include assertions to check broker responses or logs, if possible

    # def test_publish_variable_interval():
    #     client = your_mqtt_module.initialize_client()
    #     your_mqtt_module.publish_messages(client=client, period=10, variable_timing=True, max_messages=5)
    #     # Include assertions to check broker responses or logs, if possible

    # Reworked code to simulate random message publishing intervals.

    def publish_messages(self,  n_messages=3, period=10, variable_timing=False):
        try:
            for message_count in range(n_messages):
                for topic, base_message in self.topics_messages_list:
                    # Create the message to be sent
                    message = f"{base_message}-{message_count}"
                    result = self.client.publish(topic, message, qos=2)
                    # Log the result
                    if result.rc == 0:
                        self.logger.debug(f"Topic {topic}, Message {message} {result.mid} published successfully.")
                    else:
                        self.logger.error(f"Failed to publish topic {topic} message {message} {result.mid}. Return code: {result.rc}")

                    # Determine sleep time
                    if variable_timing:
                        sleep_time = random.randint(1, 60)  # Random sleep time between 1 and 60 seconds
                    else:
                        sleep_time = period

                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            self.logger.debug("Exiting publish_messages()...")
            self.client.stop()


def main():
    # To publish with random intervals, set variable_timing=True
    topics_messages_list = [
        ("cmnd/mistbuddy_fan/POWER", 1),
        ("cmnd/mistbuddy_mister/POWER", 1),
        ("cmnd/mistbuddy_fan/POWER", 0),
        ("cmnd/mistbuddy_mister/POWER", 0)
    ]
    m = MqttPublish(topics_messages_list)
    m.publish_messages(period=3)

if __name__ == "__main__":
    main()



