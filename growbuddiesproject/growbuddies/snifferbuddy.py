from mqtt_code import MQTTService
import sys


def main():

    # Define a callback function
    def on_snifferbuddy_readings(msg):
        print(f"in on_snifferbuddy_readings received message: {msg}")

    def on_snifferbuddy_status(msg):
        print(f"in on_snifferbuddy_status received message: {msg}")

    topics_and_callbacks_dict = {
        "tele/snifferbuddy/SENSOR": on_snifferbuddy_readings,
        "tele/snifferbuddy/LWT": on_snifferbuddy_status,
    }

    # Create an MQTTService instance
    mqtt_service = MQTTService(client_id="snifferbuddy", host="gus", topics_and_callbacks=topics_and_callbacks_dict)

    # Start the MQTT service
    mqtt_service.start()
    while True:
        try:
            pass
        except KeyboardInterrupt as e:
            print(f"Exiting the program...Error: {e}")
            # Stop the MQTT service
            mqtt_service.stop()
            sys.exit()


if __name__ == "__main__":
    main()
