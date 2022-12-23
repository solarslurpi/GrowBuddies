
import paho.mqtt.client as mqtt

# Import the MQTTClient and MQTTService classes
from ..mqtt_code import MQTTClient


# A callback function that can be used for testing
def test_callback(payload):
    print(f"in test_callback.  The payload is: {payload}")


def test_mqtt_client_init():
    # Test that the MQTTClient object is created correctly
    client = MQTTClient(
        client_id="test-client-id", host="test-host", topics_and_callbacks={"test-topic": test_callback}
    )
    assert client.client_id == "test-client-id"
    assert client.host == "test-host"
    assert client.topics_and_callbacks == {"test-topic": test_callback}
    assert isinstance(client.client, mqtt.Client)


def test_client_on_message():
    # Create a mock callback function to replace the real one.
    # callback = test_callback

    # Create an MQTTClient object with the mock callback function.
    topics_and_callbacks = {'test/topic': test_callback}
    client = MQTTClient(topics_and_callbacks=topics_and_callbacks)
    # Create a mock message object with the 'payload' and 'topic' attributes
    msg = {'payload': "test", 'topic': "test/topic", 'qos': 2}
    print(f"{msg.payload}")

    # Send a message to the client, providing the correct arguments for the 'userdata' and 'msg' parameters
    # client.on_message("clientid", "userdata", msg)
    # Assert that the mock callback function was called with the correct payload.
    # callback.assert_called_once_with(payload)

