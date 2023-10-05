
import time
from threading import Timer
from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings
from influxdb_code import ReadingsStore
from growbuddies.snifferbuddy_handler import SnifferBuddyHandler
from growbuddies.mqtt_publish import MqttPublish


class Mom:

    def __init__(self):
        self.logger = LoggingHandler()
        self._last_reading_time = None
        self.current_timer = None

    def log_message(self, message: str) -> None:
        self.logger.debug(message)

    def validate_readings(self, s: dict) -> dict:
        time_difference = 0.0
        current_time = time.time()
        if self._last_reading_time:
            time_difference = current_time - self._last_reading_time
        self._last_reading_time = current_time

        temp_status = self._check_temperature(s["temperature"], s["unit"])
        humidity_status = self._check_humidity(s["humidity"])
        co2_status = self._check_co2(s["co2"])
        vpd_status = self._check_vpd(s["vpd"])

        # Combine statuses into 12 bits (3 bits per status)
        combined_status = (
            (co2_status << 9) | (vpd_status << 6) | (temp_status << 3) | humidity_status
        )
        self.logger.debug(f"{time_difference:.2f}  {combined_status}")

        # Extract individual statuses
        co2_status = (combined_status >> 9) & 0b111
        vpd_status = (combined_status >> 6) & 0b111
        temp_status = (combined_status >> 3) & 0b111
        humidity_status = combined_status & 0b111

        print(f"CO2 Status: {co2_status}")
        print(f"VPD Status: {vpd_status}")
        print(f"Temperature Status: {temp_status}")
        print(f"Humidity Status: {humidity_status}")
        readings = {
            "name": s["name"],
            "version": s["version"],
            "status": combined_status,
            "temperature": s["temperature"],
            "humidity": s["humidity"],
            "vpd": s["vpd"],
            "co2": s["co2"],
            "light": s["light"],
        }
        return readings

    def _check_temperature(self, temp: float, unit: str) -> int:
        if unit == "F":
            min_temp, max_temp = 65, 90
        elif unit == "C":
            min_temp, max_temp = 18, 32
        else:
            self.logger.debug("Invalid unit")
            return 3  # INVALID UNIT

        if min_temp <= temp <= max_temp:
            return 0  # GOOD
        elif temp < min_temp:
            return 1  # TOO LOW
        else:
            return 2  # TOO HIGH

    def _check_humidity(self, humidity: float) -> int:
        min_humidity, max_humidity = 40, 70

        if min_humidity <= humidity <= max_humidity:
            return 0  # GOOD
        elif humidity < min_humidity:
            return 1  # TOO LOW
        else:
            return 2  # TOO HIGH

    def _check_co2(self, co2: float) -> int:
        min_co2, max_co2 = 400, 1300

        if min_co2 <= co2 <= max_co2:
            return 0  # GOOD
        elif co2 < min_co2:
            return 1  # TOO LOW
        else:
            return 2  # TOO HIGH

    def _check_vpd(self, vpd: float) -> int:
        # Cancel the existing timer if it is running
        if self.current_timer is not None:
            self.current_timer.cancel()
        def timer_func():
            topics_messages_list = [
                ("cmnd/mistbuddy_fan/POWER", 0),
                ("cmnd/mistbuddy_mister/POWER", 0)
            ]
            m = MqttPublish(topics_messages_list)
            m.publish_messages(n_messages=2, period=3)
            self.logger.debug("Sent delayed Power off messages.")

       # Start the timer to execute timer_func after 15 seconds
        self.current_timer = Timer(20, timer_func)
        self.current_timer.start()

        s = Settings()
        s.load()
        vpd_setpoint = s.settings["MistBuddy_PID_key"]["setpoint"]
        min_vpd = vpd_setpoint - 0.02
        max_vpd = vpd_setpoint + 0.04
        if min_vpd <= vpd <= max_vpd:
            return 0  # GOOD
        elif vpd < min_vpd:
            # If the vpd is too low, it could be that the power plugs missed an mqtt message to turn off.
            # This has been a challenge in the past, so I liberally will send power off messages.
            topics_messages_list = [
                                    ("cmnd/mistbuddy_fan/POWER", 0),
                                    ("cmnd/mistbuddy_mister/POWER", 0)
                                    ]
            m = MqttPublish(topics_messages_list)
            m.publish_messages(n_messages=1, period=0)
            self.logger.debug("Sent Power off messages.")
            return 1  # TOO LOW
        else:
            return 2  # TOO HIGH

    def send_alert(self, person: str = None) -> None:
        # TODO: Implement this method to send alerts
        pass


def main() -> None:
    mom = Mom()
    handler = SnifferBuddyHandler()
    handler.start()

    try:
        while True:
            # A message has for the type readings or status.
            # If readings, returns a SnifferBuddyReadings instance.
            message = handler.get_message_from_queue()
            if message is not None:
                message_type, message_content = message
                if message_type == "readings":
                    readings = mom.validate_readings(message_content)
                    reading_store = ReadingsStore(table_name="GrowBuddies_status")
                    reading_store.store_readings(readings)
                else:
                    mom.log_message(message_content)

    except KeyboardInterrupt:
        handler.stop()


if __name__ == "__main__":
    main()
