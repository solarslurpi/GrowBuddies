#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
import re
import socket
import time
from enum import Enum
from typing import Optional
from logginghandler import LoggingHandler
from settings_code import Settings
from mqtt_code import MQTTClient

from pydantic_config import PIDConfig
from pydantic import ValidationError


SOCKET_TIMEOUT = 120  # Number of seconds for a udp port recv() should wait for a reading from Telegraf.
READING_TIMEOUT_COUNT = 10  # Number of tries to read a value before giving up.
PAUSE_SECONDS = 60  # Number of seconds to wait after an activation in case the reading is still in range.
ACCEPTABLE_DEVIATION = (
    0.01  # Amount a value can be from the baseline to trigger an activation.
)
BASELINE_READINGS = 1

BASELINE_TIMEOUT = 900  # 15 minutes.


MistBuddy_PID_config = "MistBuddy_PID_config"
StomaBuddy_PID_config = "StomaBuddy_PID_config"


class DataState(Enum):
    START = 0
    STOP = 1
    BETWEEN = 2


class PIDFeedback:
    """
    This code helps you figure out how much the CO2 or vpd level changes - in the case of CO2 goes up, vpd goes down - when you leave the CO2 solenoid or MistBuddy on for a set number of seconds.
    """

    def __init__(
        self,
        PID_config: str,
        initial_activation_duration: int = 3,
        repetitions: int = 2,
        increment: int = 1,
        max_activation_duration: int = 10,
    ):
        self.logger = LoggingHandler()
        self.config = self._validate_config(PID_config)
        self.initial_activation_duration = initial_activation_duration
        self.repetitions = repetitions
        self.max_activation_duration = max_activation_duration
        self.last_activation_time = None
        self.increment = increment
        # Regular expression used to get the value from the telegraf line protocol.
        self.value_regex = re.compile(rf'{self.config["telegraf_fieldname"]}=([\d.]+)')
        self._init_ports()

        self.mqtt_client = MQTTClient("PID_Calibration")
        self.logger.debug(
            f"Finished initializing.  Proceed with runs of durations between {initial_activation_duration} and {max_activation_duration} seconds, incrementing {increment} after the completion of {repetitions} repetitions of a duration."
        )

    def _validate_config(self, PID_config) -> dict:
        valid_PID_configs = [MistBuddy_PID_config, StomaBuddy_PID_config]
        if PID_config not in valid_PID_configs:
            raise ValueError(f"{PID_config} is an unknown PID config")
        s = Settings()
        try:
            settings = s.load()
        except Exception as e:
            raise RuntimeError(
                f"Error: {e} Failed to load configuration settings."
            ) from e

        PID_config_dict = settings.get(PID_config)

        try:
            config = PIDConfig(**PID_config_dict)
        except ValidationError as e:
            raise ValueError(f"Validation error: {e}")

        self.logger.debug(f"--> validate_config(): Config has been validated. {config}")
        return config.model_dump()

    def _init_ports(self):
        self.incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.incoming_socket.settimeout(SOCKET_TIMEOUT)
        mean_values_port = self.config.get("mean_values_input_port")
        try:
            self.incoming_socket.bind(("localhost", mean_values_port))
        except Exception as e:
            self.incoming_socket.close()
            raise RuntimeError(
                f"Failed to bind UDP socket on port {mean_values_port}."
            ) from e
        self.output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.output_socket.settimeout(SOCKET_TIMEOUT)

    def start(self) -> None:
        self.repetition_count = 0
        self.current_activation_duration = self.initial_activation_duration
        self._establish_baseline()
        value = self._get_value()
        self._store_reading(value, self.current_activation_duration, DataState.START)
        self._process_readings()

    def _establish_baseline(self) -> None:
        self.logger.debug("--> Establishing baseline...")
        total = 0
        baseline_attempts = 0
        while baseline_attempts < BASELINE_READINGS:
            value = self._get_value()
            if value is not None:
                total += value
                baseline_attempts += 1
                self.logger.debug(f" Attempt {baseline_attempts} / {BASELINE_READINGS}")
        self.baseline_value = total / baseline_attempts
        self.logger.info(f"Baseline established: {self.baseline_value}")

    def _process_readings(self) -> None:
        self.mqtt_client.start()
        last_baseline_time = time.time()

        try:
            while self._not_finished():
                value = self._get_value()
                current_time = time.time()
                # Check if baseline is not reached within BASELINE_TIMEOUT seconds from the start of this repetition.
                if current_time - last_baseline_time > BASELINE_TIMEOUT:
                    self.logger.info(
                        "Baseline not reached within 15 minutes. Recalculating baseline."
                    )
                    # Finish this run...
                    self._store_reading(
                        value, self.current_activation_duration, DataState.STOP
                    )
                    self.repetition_count += 1
                    # Start afresh with a new baseline.
                    self._establish_baseline()
                    last_baseline_time = time.time()
                    value = self._get_value()
                    self._store_reading(
                        value, self.current_activation_duration, DataState.START
                    )
                    last_baseline_time = time.time()

                if self._is_time_to_activate(value):
                    # Stop this run.
                    self._store_reading(
                        # Turn the actuator's power on...
                        value,
                        self.current_activation_duration,
                        DataState.STOP,
                    )
                    self.repetition_count += 1
                    self._turn_on_power(self.current_activation_duration)
                    # Start collecting data points for the new run.
                    value = self._get_value()
                    self._store_reading(
                        value, self.current_activation_duration, DataState.START
                    )
                    last_baseline_time = time.time()
                else:
                    self._store_reading(
                        value, self.current_activation_duration, DataState.BETWEEN
                    )
        except KeyboardInterrupt:
            self.logger.info("User interrupted the process. Exiting...")
            self.cleanup()

    def _is_time_to_activate(self, value: float) -> bool:
        # TODO: CURRENTLY HARDCODED TO CO2.
        upper_limit = self.baseline_value + ACCEPTABLE_DEVIATION * self.baseline_value
        self.logger.debug(f"Value: {value}....Baseline value: {upper_limit}....")
        if value <= upper_limit:
            self.logger.debug("Time to activate!")
            return True
        self.logger.debug("Not time to activate.")
        return False

    def _not_finished(self) -> bool:
        if self.repetition_count >= self.repetitions:
            self.repetition_count = 0
            self.current_activation_duration += self.increment

            if self.current_activation_duration > self.max_activation_duration:
                self.logger.info("Process completed.")
                self.cleanup()  # Perform any necessary cleanup
                return False

        return True

    def _turn_on_power(self, seconds_on: float) -> None:
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
            self._settle_down(PAUSE_SECONDS)

    def _settle_down(self, pause_seconds: int) -> None:
        end_time = time.time() + pause_seconds
        og_timeout = self.incoming_socket.gettimeout()
        while time.time() < end_time:
            try:
                # Set the socket to non-blocking with a timeout
                self.incoming_socket.settimeout(end_time - time.time())
                packet = self.incoming_socket.recv(1024)
                self.logger.debug(f"Read in packet while pausing: {packet.decode()}")
                # Process the packet here if needed
            except socket.timeout:
                # When a timeout exception occurs, it typically means no more data is available to read within the specified timeout period.  The socket's buffer is empty.
                self.logger.debug("Socket timeout waiting while pausing...")
            except socket.error as e:
                # Other socket errors might occur due to various reasons (e.g., network issues, socket being closed unexpectedly, etc.). In the context of flushing the socket buffer, these errors indicate that we cannot continue reading from the socket as intended.  We've done our best to clear the buffer, but due to some error, we can't guarantee that all buffered data has been read. The function will exit, avoiding any potential hang or crash.
                self.logger.error(f"Socket error during pause: {e}")
        self.incoming_socket.settimeout(og_timeout)

    def _get_value(self) -> Optional[float]:
        value = None
        while not value:
            try:
                packet = self.incoming_socket.recv(1024)
                decoded_str = packet.decode()
                self.logger.debug(f"Incoming packet: {decoded_str}")

                value_match = self.value_regex.search(decoded_str)
                if value_match:
                    value = float(value_match.group(1))
                    return value
                else:
                    self.logger.warning(
                        "Value format mismatch in packet received from Telegraf"
                    )
            except socket.timeout:
                self.logger.error("Socket timeout occurred in get_value")
            except socket.error as e:
                self.logger.error(f"Socket error in get_value: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error in get_value: {e}")

    def _store_reading(
        self, reading: float, duration: int, data_state: DataState
    ) -> None:
        # Decode the bytes into a string.
        int_data_state = data_state.value
        line_protocol = f"pid_feedback value={reading},duration={duration},data_state={int_data_state},baseline={self.baseline_value}"
        self.logger.debug(f"Reading: {line_protocol}")

        # Convert the line protocol string to bytes
        message = line_protocol.encode("utf-8")

        # Send the data
        # Assuming 'self.output_socket' is a UDP socket already created
        port = self.config.get("store_readings_output_port")
        try:
            self.output_socket.sendto(message, ("localhost", port))
        except Exception as e:
            self.logger.error(f"Error in store_reading: {e}")

    def cleanup(self) -> None:
        self.incoming_socket.close()
        self.output_socket.close()
        self.mqtt_client.stop()


feedback = PIDFeedback("StomaBuddy_PID_config")
feedback.start()
