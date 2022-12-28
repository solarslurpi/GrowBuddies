import paho.mqtt.client as mqtt
import time


# Define a function to send the MQTT message
def send_message(client, topic, message):
    client.publish(topic, message)


# Create a new MQTT client
client = mqtt.Client()
while True:
    # Connect to the MQTT broker
    client.connect("gus")
    # Send the first MQTT message
    send_message(client, "cmnd/mistbuddy_fan/POWER", "ON")
    send_message(client, "cmnd/mistbuddy_mister/POWER", "ON")
    # Wait a bit...
    time.sleep(13)
    send_message(client, "cmnd/mistbuddy_fan/POWER", "OFF")
    send_message(client, "cmnd/mistbuddy_mister/POWER", "OFF")
    client.disconnect()
    time.sleep(60 - 13)
