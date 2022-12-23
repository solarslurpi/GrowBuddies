import paho.mqtt.client as mqtt
import time

# Set the MQTT broker and topic
broker = "gus"
fan_topic = "test/topic"
mist_topic = "...."


# Define a function to send the MQTT message
def send_message(client, topic, message):
    client.publish(topic, message)


# Create a new MQTT client
client = mqtt.Client()
while True:
    # Connect to the MQTT broker
    client.connect(broker)
    # Send the first MQTT message
    send_message(client, "cmnd/mistbuddy_fan/POWER", "ON")
    send_message(client, "cmnd/mistbuddy_mister/POWER", "ON")
    # Wait a bit...
    time.sleep(8)
    send_message(client, "cmnd/mistbuddy_fan/POWER", "OFF")
    send_message(client, "cmnd/mistbuddy_mister/POWER", "OFF")
    client.disconnect()
    time.sleep(52)
