import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from ..gus_new import MQTTClient


# Helper function to mock the InfluxDBClient.write_points method
def mock_write_points(data):
    pass


# Helper function to create a mock MQTTClient instance
def mock_mqtt_client(mock_connect=True, mock_disconnect=True):
    client = mqtt.Client()
    client.connect = lambda *args: mock_connect
    client.disconnect = lambda *args: mock_disconnect
    return client


# Helper function to create a mock InfluxDBClient instance
def mock_influxdb_client(mock_write_points):
    client = InfluxDBClient()
    client.write_points = mock_write_points
    return client


def test_MQTTClient_init():
    # Test the MQTTClient constructor with valid input
    client = MQTTClient(client_id="test_client", host="test_host", port=1883, lwt_topic="/lwt", lwt_message="offline")
    assert client.client_id == "test_client"
    assert client.host == "test_host"
    assert client.port == 1883
    assert client.lwt_topic == "/lwt"
    assert client.lwt_message == "offline"


# def test_MQTTClient_on_connect():
#     # Test the MQTTClient.on_connect method
#     client = MQTTClient(client_id="test_client", host="test_host", port=1883, lwt_topic="/lwt", lwt_message="offline")
#     client.client = mock_mqtt_client()
#     client.on_connect(client.client, None, None, 0)
#     assert "tele/snifferbuddy/SENSOR" in client.client.subscriptions()


def test_MQTTClient_on_disconnect():
    # Test the MQTTClient.on_disconnect method
    client = MQTTClient(client_id="test_client", host="test_host", port=1883, lwt_topic="/lwt", lwt_message="offline")
    client.on_disconnect(None, None, 0)
    client.on_disconnect(None, None, 1)


def test_MQTTClient_on_message():
    # Test the MQTTClient.on_message method
    client = MQTTClient(client_id="test_client", host="test_host", port=1883, lwt_topic="/lwt", lwt_message="offline")
    client.client = mock_mqtt_client()
    client.store_reading = lambda x, y: None
    client.on_message(client.client, None, mqtt.MQTTMessage("test_topic", b"test_payload"))


def test_MQTTClient_store_reading():
    # Test the MQTTClient.store_reading method
    client = MQTTClient(client_id="test_client", host="test_host", port=1883, lwt_topic="/lwt", lwt_message="offline")

    # Mock the InfluxDBClient.write_points method
    mock_write_points = lambda x: None
    client.influxdb_client = mock_influxdb_client(mock_write_points)

    # Call the store_reading method with valid input
    client.store_reading("my_table", {"CO2": 90, "temp": 72})

    # Assert that the InfluxDBClient.write_points method was called
    assert client.influxdb_client.write_points.called
