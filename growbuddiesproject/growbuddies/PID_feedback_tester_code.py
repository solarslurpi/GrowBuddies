#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
import re
import socket
import time
from common import COMPARISON_FUNCTIONS
from logginghandler import LoggingHandler
from settings_code import Settings
from mqtt_code import MQTTClient

SOCKET_TIMEOUT = 120  # Number of seconds for a udp port recv() should wait for a reading from Telegraf.
READING_TIMEOUT_COUNT = 10  # Number of tries to read a value before giving up.
PAUSE_SECONDS = 30  # Number of seconds to wait after an activation in case the reading is still in range.
ACCEPTABLE_DEVIATION = (
    0.03  # Amount a value can be from the baseline to trigger an activation.
)


MistBuddy_PID_config = "MistBuddy_PID_config"
StomaBuddy_PID_config = "StomaBuddy_PID_config"


class PIDFeedbackTester:
    """
    This code helps you figure out how much the CO2 or vpd level changes - in the case of CO2 goes up, vpd goes down - when you leave the CO2 solenoid or MistBuddy on for a set number of seconds.
    """

    def __init__(
        self,
        PID_config: str,
        initial_activation_duration: int = 3,
        repetitions: int = 3,
        increment: int = 1,
        max_activation_duration: int = 10,
    ):
        self.logger = LoggingHandler()
        self.config = self._validate_config(PID_config)
        self.initial_activation_duration = initial_activation_duration
        self.repetitions = repetitions
        self.max_activation_duration = max_activation_duration
        self.increment = increment
        self._init_ports()
        # Regular expression used to get the value from the telegraf line protocol.
        self.value_regex = re.compile(rf'{self.config["telegraf_fieldname"]}=([\d.]+)')
        self.mqtt_client = MQTTClient("PID_Calibration")

    def _validate_config(self, PID_config) -> dict:
        config = {}
        # Focus on StomaBuddy and MistBuddy..it's what we know.
        if PID_config not in (MistBuddy_PID_config, StomaBuddy_PID_config):
            raise ValueError(
                f" Error: {PID_config} is not valid.  Valid configuration names are {MistBuddy_PID_config} and {StomaBuddy_PID_config}."
            )
        # Get the config file
        s = Settings()
        try:
            settings = s.load()
        except Exception as e:
            raise RuntimeError("Failed to load configuration settings.") from e
        PID_config_dict = settings.get(PID_config)
        try:
            # Validate ports are integers and within the correct range
            config["store_readings_port"] = int(
                PID_config_dict.get("calibrate_udp_out_port")
            )
            if not (0 < config["store_readings_port"] < 65536):
                raise ValueError("store_readings_port out of range")

            config["incoming_port"] = int(PID_config_dict.get("PID_values_port"))
            if not (0 < config["incoming_port"] < 65536):
                raise ValueError("incoming_port out of range")

            # Validate telegraf fieldname is a non-empty string
            config["telegraf_fieldname"] = str(
                PID_config_dict.get("telegraf_fieldname")
            )
            if not config["telegraf_fieldname"]:
                raise ValueError("telegraf_fieldname is empty")

            # Validate MQTT topics
            config["mqtt_power_topics"] = PID_config_dict.get("mqtt", "")
            if not config["mqtt_power_topics"]:
                raise ValueError("mqtt_power_topics is empty")

            # Validate device name is extracted correctly and is one of the known devices
            config["device_name"] = PID_config.split("_")[0]
            if config["device_name"] not in ["MistBuddy", "StomaBuddy"]:
                raise ValueError("Unknown device name extracted")

            config["within_function"] = COMPARISON_FUNCTIONS.get("within_range")
            if not config["within_function"]:
                raise ValueError("within_function is empty")

        except ValueError as e:
            raise ValueError(f"Validation error: {e}")
        self.logger.debug(f"--> validate_config(): Config has been validated. {config}")
        return config

    def _init_ports(self):
        self.incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.incoming_socket.settimeout(SOCKET_TIMEOUT)
        incoming_port = self.config["incoming_port"]
        try:
            self.incoming_socket.bind(("localhost", incoming_port))
        except Exception as e:
            self.incoming_socket.close()
            raise RuntimeError(
                f"Failed to bind UDP socket on port {incoming_port}."
            ) from e
        self.output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.output_socket.settimeout(SOCKET_TIMEOUT)

    def start(self):
        def _init_loop_vars():
            self.repetition_count = 0
            self.current_activation_duration = self.initial_activation_duration

        def _start_listening():
            # This is single purpose so decided against adding a thread...
            # self.stop_requested = threading.Event()
            # self.listening_thread = threading.Thread(
            #     target=self._process_readings, daemon=True
            # )
            # self.listening_thread.start()
            self._process_readings()

        _init_loop_vars()
        _start_listening()

    def _process_readings(self):
        def _handle_baseline_reading():
            baseline_value = None
            count = 0
            while not baseline_value:
                baseline_value = self._get_value()
                if baseline_value:
                    self._store_reading(baseline_value, 0)
                    self._turn_on_power(self.current_activation_duration)
                    return baseline_value
                count += 1
                if count > READING_TIMEOUT_COUNT:
                    raise Exception(
                        "Failed to get value from packet after several attempts."
                    )

        def _handle_calibration_readings(baseline_value):
            tolerance = ACCEPTABLE_DEVIATION * baseline_value
            min_val = baseline_value - tolerance
            max_val = baseline_value + tolerance
            within_function = self.config.get("within_function")
            last_activation_time = None

            try:
                while self.current_activation_duration <= self.max_activation_duration:
                    self.logger.debug(
                        f"Current activation duration: {self.current_activation_duration}....Max duration: {self.max_activation_duration}"
                    )
                    value = self._get_value()
                    if value is not None:
                        self._store_reading(value, self.current_activation_duration)
                        current_time = time.time()
                        if within_function(value, min_val, max_val):
                            self.logger.debug("Within tolerance.")
                            if (
                                last_activation_time is None
                                or (current_time - last_activation_time) > PAUSE_SECONDS
                            ):
                                self.logger.debug(
                                    f"Last activation time is greater than {PAUSE_SECONDS} seconds."
                                )
                                self._turn_on_power(self.current_activation_duration)
                                last_activation_time = current_time
                                self.repetition_count += 1
                            if self.repetition_count >= self.repetitions:
                                self.repetition_count = 0
                                self.current_activation_duration += self.increment
                        else:
                            continue

                    else:
                        self.logger.error("Error: Received None value.")
            except KeyboardInterrupt:
                self.logger.info("User interrupted the process. Exiting...")
                self.cleanup()

        self.mqtt_client.start()  # Start mqtt in same thread.
        baseline_value = _handle_baseline_reading()
        _handle_calibration_readings(baseline_value)

    def _turn_on_power(self, seconds_on):
        self._publish_power_plug_messages(seconds_on)

    def _publish_power_plug_messages(self, seconds_on: float) -> None:
        """
        Publish MQTT messages to control the power state.

        Args:
            power_state (int): Desired power state, either 1 (for on) or 0.
        """
        for power_command in self.config.get("mqtt_power_topics"):
            self.logger.debug(f"POWER ON for {seconds_on} seconds.")
            self.mqtt_client.publish(
                power_command, 1, qos=1
            )  # Sending 1 turns on power
            # Split the topic by the '/'
            parts = power_command.split("/")
            # Replace the last part with 'PulseTime'
            parts[-1] = "PulseTime"
            # Join the parts back together to form the new topic
            pulsetime_command = "/".join(parts)
            # I find this confusing, but from the Tasmota docs:
            # 1..111 = set PulseTime for Relay<x> in 0.1 second increments
            # 112..64900 = set PulseTime for Relay<x>, offset by 100, in 1 second increments. Add 100 to desired interval in seconds, e.g., PulseTime 113 = 13 seconds and PulseTime 460 = 6 minutes (i.e., 360 seconds)
            if seconds_on < 11:
                pulsetime_on = seconds_on * 10
            else:
                pulsetime_on = seconds_on + 100
            # This tells Tasmota to turn
            self.mqtt_client.publish(pulsetime_command, pulsetime_on, qos=1)

    def _get_value(self):
        try:
            packet = self.incoming_socket.recv(1024)
            decoded_str = packet.decode()
            # Retrive the value from the Telegraf line protocol.
            value_match = self.value_regex.search(decoded_str)
            if value_match:
                value = float(value_match.group(1))
                return value
            else:
                self.logger.warning(
                    "Value format mismatch in packet received from Telegraf"
                )
                return None
        except socket.timeout:
            self.logger.error("Socket timeout occurred in get_value")
            return None
        except socket.error as e:
            self.logger.error(f"Socket error in get_value: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in get_value: {e}")
            return None

    def _store_reading(self, reading, duration: int) -> None:
        # Decode the bytes into a string.
        line_protocol = f'calibration,device={self.config.get("device_name")} value={reading},duration={duration}'
        self.logger.debug(f"Reading to be published: {line_protocol}")

        # Convert the line protocol string to bytes
        message = line_protocol.encode("utf-8")

        # Send the data
        # Assuming 'self.output_socket' is a UDP socket already created and connected to Telegraf's UDP port
        try:
            self.output_socket.sendto(
                message, ("localhost", self.config.get("store_readings_port"))
            )
        except Exception as e:
            self.logger.error(f"Error in store_reading: {e}")

    def cleanup(self):
        self._stop()
        self.incoming_socket.close()
        self.output_socket.close()
        self.mqtt_client.stop()

    def _stop(self):
        pass
        # Signal the process_readings thread to complete its current iteration and stop
        # self.stop_requested.set()
        # if self.listening_thread.is_alive():
        #     self.listening_thread.join()


calibrator = PIDFeedbackTester("StomaBuddy_PID_config")
calibrator.start()
