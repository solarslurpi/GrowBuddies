#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
import re
import socket
import threading
from logginghandler import LoggingHandler
from settings_code import Settings
from mqtt_code import MQTTClient

SOCKET_TIMEOUT = 120 # Number of seconds for a udp port recv() should wait for a reading from Telegraf.

MistBuddy_PID_config = "MistBuddy_PID_config"
StomaBuddy_PID_config = "StomaBuddy_PID_config"

class PIDCalibrator:
    """
    This code helps you figure out how much the CO2 or vpd level changes - in the case of CO2 goes up, vpd goes down - when you leave the CO2 solenoid or MistBuddy on for a set number of seconds.
    """
    def __init__(self, PID_config:str, initial_activation_duration:int=2, repetitions:int=5, increment:int=2, max_activation_duration:int=15):
        self.logger = LoggingHandler()
        self.config = self.validate_config(PID_config)
        self.initial_activation_duration = initial_activation_duration
        self.repetitions = repetitions
        self.max_activation_duration = max_activation_duration
        self.increment = increment
        self.init_ports()
        self.connect_mqtt_client()

    def connect_mqtt_client(self):
        self.mqtt_client = MQTTClient("PID_Calibration")
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        try:
            self.mqtt_client.connect()
            self.logger.debug("MQTT client connect attempt.")
        except Exception as e:
            self.logger.error("Failed to connect MQTT client.")
            raise IOError("Failed to connect to MQTT broker") from e

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.debug(f"Connected to MQTT broker with result code {rc}")
            self.mqtt_client.loop_start()
        else:
            self.logger.warning(f"Failed to connect to MQTT broker, return code {rc}")
            # Implement reconnection logic if needed

    def on_mqtt_disconnect(self, client, userdata, rc):
        self.logger.info(f"Disconnected from MQTT broker with result code {rc}")

    def validate_config(self, PID_config) -> dict:
        config = {}
        # Focus on StomaBuddy and MistBuddy..it's what we know.
        if PID_config not in (MistBuddy_PID_config, StomaBuddy_PID_config):
            raise ValueError(f" Error: {PID_config} is not valid.  Valid configuration names are {MistBuddy_PID_config} and {StomaBuddy_PID_config}.")
        # Get the config file
        s = Settings()
        try:
            settings = s.load()
        except Exception as e:
            raise RuntimeError("Failed to load configuration settings.") from e
        PID_config_dict = settings.get(PID_config)
        try:
            # Validate ports are integers and within the correct range
            config["store_readings_port"] = int(PID_config_dict.get("calibrate_udp_out_port"))
            if not (0 < config["store_readings_port"] < 65536):
                raise ValueError("store_readings_port out of range")

            config["incoming_port"] = int(PID_config_dict.get("PID_values_port"))
            if not (0 < config["incoming_port"] < 65536):
                raise ValueError("incoming_port out of range")

            # Validate telegraf fieldname is a non-empty string
            config["telegraf_fieldname"] = str(PID_config_dict.get("telegraf_fieldname"))
            if not config["telegraf_fieldname"]:
                raise ValueError("telegraf_fieldname is empty")

            # Validate MQTT topics
            config["mqtt_power_topics"] = str(PID_config_dict.get("mqtt",""))
            if not config["mqtt_power_topics"]:
                raise ValueError("mqtt_power_topics is empty")

            # Validate device name is extracted correctly and is one of the known devices
            config["device_name"] = PID_config.split('_')[0]
            if config["device_name"] not in ["MistBuddy", "StomaBuddy"]:
                raise ValueError("Unknown device name extracted")
        except ValueError as e:
            raise ValueError (f"Validation error: {e}")
        self.logger.debug(f"--> validate_config(): Config has been validated. {config}")
        return config

    def init_ports(self):
        self.incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.incoming_socket.settimeout(SOCKET_TIMEOUT)
        incoming_port = self.config["incoming_port"]
        try:
            self.incoming_socket.bind( ("localhost", incoming_port) )
        except Exception as e:
            self.incoming_socket.close()
            raise RuntimeError(f"Failed to bind UDP socket on port {incoming_port}.") from e
        self.output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.output_socket.settimeout(SOCKET_TIMEOUT)


    def start_process(self):
        def _init_loop_vars():
            self.current_repetition = 0
            self.current_activation_duration = self.initial_activation_duration
        def _start_listening():
            listening_thread = threading.Thread(target=self.process_reading)
            listening_thread.start()
        _init_loop_vars()
        _start_listening()


    def process_reading(self):
        def _handle_baseline_reading():
            baseline_value = None
            count = 0
            while not baseline_value:
                baseline_value = self.get_value()
                if baseline_value:
                    self.store_reading(baseline_value,0)
                    self.turn_on_power(self.current_activation_duration)
                    return baseline_value
                count+= 1
                if count > 10: #10 is an arbitrary number....
                    raise Exception("Failed to get value from packet after several attempts.")
        baseline_value = _handle_baseline_reading()
        bValue_stored = False
        # Calculate 5% of the baseline value
        tolerance = 0.05 * baseline_value
        while self.current_activation_duration <= self.max_activation_duration:
            # Listening for readings from the port we set up with Telegraf.
            value  = self.get_value() # Buffer size is 1024 bytes
            if not bValue_stored:
                self.store_reading(value,self.current_activation_duration)
                bValue_stored = True
            # Check if the value is within ±5% of the baseline value
            if abs(value - baseline_value) <= tolerance:
                self.turn_on_power(self.current_activation_duration)
                self.current_repetition += 1
                self.bValueStored = False
            else: # current level is either too high (CO2) or too low (vpd)
                continue

            # Check if the current solenoid time has been repeated enough times
            if self.current_repetition >= self.repetitions:
                # Reset for the next solenoid open time being tested.
                self.current_repetition = 0
                # Add more time for the solenoid to be open.
                self.current_activation_duration += self.increment
        self.cleanup()

    def turn_on_power(self, seconds_on):
        self.mqtt_client.start()
        self._publish_power_plug_messages(seconds_on)
        self.mqtt_client.stop()

    def _publish_power_plug_messages(self, seconds_on: float) -> None:
        """
        Publish MQTT messages to control the power state.

        Args:
            power_state (int): Desired power state, either 1 (for on) or 0.
        """
        for power_command in self.config.get("mqtt_power_topics"):
            self.logger.debug(f"POWER ON for {seconds_on} seconds.")
            self.mqtt_client.publish(power_command, 1, qos=1) # Sending 1 turns on power
            # Split the topic by the '/'
            parts = power_command.split('/')
            # Replace the last part with 'PulseTime'
            parts[-1] = "PulseTime"
            # Join the parts back together to form the new topic
            pulsetime_command = '/'.join(parts)
            # I find this confusing, but from the Tasmota docs:
            # 1..111 = set PulseTime for Relay<x> in 0.1 second increments
            #112..64900 = set PulseTime for Relay<x>, offset by 100, in 1 second increments. Add 100 to desired interval in seconds, e.g., PulseTime 113 = 13 seconds and PulseTime 460 = 6 minutes (i.e., 360 seconds)
            if seconds_on< 11:
                pulsetime_on = seconds_on * 10
            else:
                pulsetime_on = seconds_on + 100
            # This tells Tasmota to turn
            self.mqtt_client.publish(pulsetime_command, pulsetime_on, qos=1)

    def get_value(self):
        packet = self.incoming_socket.recv(1024)
        decoded_str = packet.decode()
        # Retrive the value
        value_regex = re.compile(fr'{self.config.get["telegraf_fieldname"]}=([\d.]+)')
        value_match = value_regex.search(decoded_str)
        if value_match:
            value = float(value_match.group(1))
            return value
        else:
            self.logger.warning("Could not find value within packet received from Telegraf")
            return None


    def store_reading(self, reading, duration: int) -> None:
        # Decode the bytes into a string.


            line_protocol = f'calibration,device={self.config.get("device_name")} value={reading},duration={duration}'
            self.logger.debug(f'Reading to be published: {line_protocol}')

            # Convert the line protocol string to bytes
            message = line_protocol.encode('utf-8')

            # Send the data
            # Assuming 'self.output_socket' is a UDP socket already created and connected to Telegraf's UDP port
            self.output_socket.sendto(message, ("localhost", self.config.get("store_readings_port") ))
            return reading


    def cleanup(self):
        self.incoming_socket.close()
        self.output_socket.close()
        self.mqtt_client.disconnect()

calibrator = PIDCalibrator("StomaBuddy_PID_config")
calibrator.start()