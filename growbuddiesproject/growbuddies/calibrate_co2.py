import csv
import sys
import threading
import os.path
from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings
from growbuddies.mqtt_code import MQTTService, MQTTClient
from growbuddies.snifferbuddyreadings_code import SnifferBuddyReadings
import time


class Callbacks:
    def __init__(self, max_readings):
        self.logger = LoggingHandler()
        self.readings_received = 0
        self.max_readings = max_readings
        self.logger.debug(f"{self.max_readings} will be taken.")
        self._mqtt_service = None

        # create a list to store the CO2 readings
        self.co2_readings = []

    @property
    def mqtt_service(self):
        return self._mqtt_service

    @mqtt_service.setter
    def mqtt_service(self, value):
        self._mqtt_service = value

    def on_snifferbuddy_readings(self, msg):
        s = SnifferBuddyReadings(msg)
        if s.valid_packet:
            self.logger.debug(f"The co2 level is: {s.co2}")
            self.logger.debug("The CO2 solenoid will be turned ON for 3 Seconds.")
            self.turn_on_stomaBuddy(3)

            # add the current CO2 reading to the list
            self.co2_readings.append(s.co2)

            self.readings_received += 1
            self.logger.debug(f"The number of readings received is {self.readings_received}")
            if self.readings_received >= self.max_readings:
                # calculate the differences between the current and previous CO2 readings
                diffs = [self.co2_readings[i] - self.co2_readings[i - 1] for i in range(1, len(self.co2_readings))]

                # create a list of tuples that contains the current and previous CO2 readings, and their differences
                co2_data = list(zip(self.co2_readings[1:], self.co2_readings[:-1], diffs))

                # check if the file exists
                file_exists = os.path.isfile("co2_data.csv")

                # write the CO2 data to the file
                with open("co2_data.csv", "a+", newline="") as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(["current_co2", "previous_co2", "difference"])
                    for row in co2_data:
                        writer.writerow(row)

                self.mqtt_service.stop()
                sys.exit()

    def on_snifferbuddy_status(self, status):
        self.logger.debug(f"-> SnifferBuddy is: {status}")

    def turn_on_stomaBuddy(self, nSecondsON: int) -> None:
        """Sends an mqtt messages to mistBuddy's two power sources plugged into Tasmotized Smart plugs, a fan and a mister.
        The self.fan_power_topic and self.mister_power_topic are set in the __init__ method.

        Args:
            nSecondsON (int): The number of seconds to turn the plugs on.

        A timer is started based on the number of seconds MistBuddy should be on.  When the timer expires, the  _turn_off_mistBuddy
        method is called. A connection to the mqtt broker is made, and the mqtt message payload "ON" is sent to the two plugs.
        """

        # The command to a Sonoff plug can be either TOGGLE, ON, OFF.
        # Send the command to power ON.
        mqtt_client = MQTTClient("StomaBuddy")
        mqtt_client.start()
        # Randomly the fan would not be turned off.  I added a sleep to see if that helps within turning on
        # as well as turning off.
        time.sleep(0.25)
        mqtt_client.publish("cmnd/stomabuddy/POWER", "ON")
        # Set up a timer with the callback on completion.
        timer = threading.Timer(nSecondsON, self.turn_off_stomaBuddy)
        time.sleep(0.25)
        mqtt_client.stop()
        self.logger.debug(
            f"...Sent mqtt message to the co2 power plug (stomabuddy) to turn ON for {nSecondsON} seconds."
        )
        timer.start()

    def turn_off_stomaBuddy(self) -> None:
        """The timer set in _turn_on_mistBuddy has expired.  Send messages to the
        mistBuddy plugs to turn OFF."""
        mqtt_client = MQTTClient("MistBuddy")
        time.sleep(0.25)
        mqtt_client.start()
        time.sleep(0.25)
        mqtt_client.publish("cmnd/stomabuddy/POWER", "OFF")
        time.sleep(0.25)
        mqtt_client.stop()
        self.logger.debug("...Sent mqtt messages to the CO2 plug (stomabuddy) to turn OFF.")


def main():
    max_readings = int(input("Enter the number of SnifferBuddy readings to receive: "))
    settings = Settings()
    settings.load()
    obj = Callbacks(max_readings)
    methods = settings.get_callbacks("snifferbuddy_mqtt", obj)
    mqtt_service = MQTTService(methods)
    obj.mqtt_service = mqtt_service
    mqtt_service.start()
    while True:
        try:
            pass
        except KeyboardInterrupt:
            mqtt_service.stop()
            sys.exit()


if __name__ == "__main__":
    main()
