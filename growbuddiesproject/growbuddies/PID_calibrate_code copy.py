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


MistBuddy_PID_config = "MistBuddy_PID_config"
StomaBuddy_PID_config = "StomaBuddy_PID_config"

class PIDCalibrator:
    """
    This code helps you figure out how much the CO2 or vpd level changes - in the case of CO2 goes up, vpd goes down - when you leave the CO2 solenoid or MistBuddy on for a set number of seconds.
    """
    def __init__(self, PID_config:str, initial_activation_duration:int=2, repetitions:int=5, increment:int=2, max_activation_duration:int=15):
        """

        Args:
            PID_config (_type_): The config file (growbuddies_settings.json) has a configuration for both PID control of CO2 (StomaBuddy_PID_config) and vpd (MistBuddy_PID_config)
            initial_activation_time (int, optional): This parameter specifies the duration, in seconds, for the initial activation of the environmental control devices at the beginning of the run cycle. Defaults to 2.
            repetitions (int, optional): _description_. Defaults to 5.
            increment (int, optional): _description_. Defaults to 2.
            max_solenoid_on (int, optional): _description_. Defaults to 15.

        Raises:
            ValueError: _description_
        """
        # Focus on StomaBuddy and MistBuddy..it's what we know.
        if PID_config not in (MistBuddy_PID_config, StomaBuddy_PID_config):
            raise ValueError(f" Error: {PID_config} is not valid.  Valid configuration names are {MistBuddy_PID_config} and {StomaBuddy_PID_config}.")
        self.logger = LoggingHandler()
        # Get the config file
        settings = Settings()
        try:
            self.config = settings.load()
        except Exception as e:
            raise RuntimeError("Failed to load configuration settings.") from e
        self.pid_settings_dict = self.config.get(PID_config,"")
        # Set up the UDP port that will receive readings
        PID_values_in_port = self.pid_settings_dict.get("PID_values_port")
        if not PID_values_in_port:
            raise RuntimeError("Failed to read the PID_values_port from the config file.")
        self.udp_out_port = self.pid_settings_dict.get("calibrate_udp_out_port")
        if not self.udp_out_port:
            raise RuntimeError("Failed to read the calibrate_udp_out_port from the config file.")
        self.repetitions = repetitions
        self.increment = increment
        self.readings_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.readings_socket.bind( ("localhost", PID_values_in_port) )
        except socket.error as e:
            self.readings_socket.close()
            raise RuntimeError(f"Failed to bind UDP socket on port {PID_values_in_port}.") from e
        self.output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.current_repetition = 0
        self.current_activation_duration = initial_activation_duration
        self.max_activation_duration = max_activation_duration
        self.telegraf_fieldname = self.pid_settings_dict.get("telegraf_fieldname")
        self.mqtt_client = MQTTClient("PID_Calibration")
        self.mqtt_power_topics = self.pid_settings_dict.get("mqtt","")
        self.device_name  = PID_config.split('_')[0]  # Extracts 'MistBuddy' or 'StomaBuddy'



    def start(self):

        listening_thread = threading.Thread(target=self.process_reading)
        listening_thread.start()

    def process_reading(self):
        # Record the baseline reading with zero activation duration
        packet = self.readings_socket.recv(1024)
        self.store_reading(packet,0)
        while self.current_activation_duration <= self.max_activation_duration:
            # Listening for readings from the port we set up with Telegraf.
            packet = self.readings_socket.recv(1024)  # Buffer size is 1024 bytes
            self.store_reading(packet,self.current_activation_duration)
            # Turn on the solenoid
            self.turn_on_power(self.current_activation_duration)
            self.current_repetition += 1

            # Check if the current solenoid time has been repeated enough times
            if self.current_repetition >= self.repetitions:
                # Reset for the next solenoid open time being tested.
                self.current_repetition = 0
                # Add more time for the solenoid to be open.
                self.current_activation_duration += self.increment

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
        for power_command in self.mqtt_power_topics:
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

    def store_reading(self, packet:bytes, duration: int) -> None:
        # Decode the bytes into a string.
        decoded_str = packet.decode()
        # Retrive the value
        value_regex = re.compile(fr'{self.telegraf_fieldname}=([\d.]+)')
        value_match = value_regex.search(decoded_str)
        if value_match:
            reading = float(value_match.group(1))
            line_protocol = f'calibration,device={self.device_name} value={reading},duration={duration}'
            self.logger.debug(f'Reading to be published: {line_protocol}')

            # Convert the line protocol string to bytes
            message = line_protocol.encode('utf-8')

            # Send the data
            # Assuming 'self.output_socket' is a UDP socket already created and connected to Telegraf's UDP port
            self.output_socket.sendto(message, ("localhost", self.udp_out_port) )

calibrator = PIDCalibrator("StomaBuddy_PID_config")
calibrator.start()