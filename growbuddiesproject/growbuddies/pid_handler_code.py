#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################

from PID_code import PID
from logginghandler import LoggingHandler
from settings_code import Settings
from mqtt_code import MQTTClient
import json
import re
import socket


MistBuddy_PID_config = "MistBuddy_PID_config"
StomaBuddy_PID_config = "StomaBuddy_PID_config"

class PIDHandler:
    def __init__(self, PID_config: str = None) -> None:
        if PID_config not in (MistBuddy_PID_config, StomaBuddy_PID_config):
            raise ValueError(f" Error: {PID_config} is not valid.  Valid configuration names are {MistBuddy_PID_config} and {StomaBuddy_PID_config}.")
        self.logger = LoggingHandler()
        settings = Settings()
        self.config = settings.load()
        self.pid_settings_dict = self.config.get(PID_config,"")
        self.telegraf_fieldname = self.pid_settings_dict.get("telegraf_fieldname")
        self.pid = PID(self.pid_settings_dict, self._handle_tuning)
        self.name = self.pid_settings_dict.get("name")
        self.mqtt_client = MQTTClient("PID_Tuning")
        self.mqtt_power_topics = self.pid_settings_dict.get("mqtt","")
        self.incoming_udp_port = self.pid_settings_dict.get("incoming_udp_port","")
        # Create a UDP socket in the casethe PID is in tuning mode (i.e.: tune_increment > 0 in growbuddysettings.json)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = ('localhost',self.pid_settings_dict.get("tune_udp_port"))
        self.logger.debug(f"Finished PIDHandler init. PID_config is {self.pid_settings_dict}")


    def start(self):
        # If this is for a tuning run, start tuning
        if self.pid_settings_dict.get("tune_increment") > 0:
            self.pid.start_tuning()
        values_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #optval = 1
        # Set the SO_REUSEPORT option at the socket level (SOL_SOCKET) to the value stored in optval (which is 1, meaning 'enabled').
        # Enabling the SO_REUSEPORT socket option before binding allows multiple instances to bind to the same UDP.
        # I tried this and although both apps can bind to the same topic, the first app that bound to the port got the packets.  The
        # second lost out, receiving no packets.  Bummer.
        #values_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, optval)
        host = '127.0.0.1'
        values_socket.bind((host, self.incoming_udp_port))
        self.logger.debug(f" Listening on port {self.incoming_udp_port}")
        while True:
            # NOTE: This code is brittle if the format of the udp packet changes,
            # This code breaks.  I'm trying to accomodate telegraf...
            # Using recv (if only the data is required)

            packet = values_socket.recv(1024)
            # Step 1: Decode the bytes
            decoded_str = packet.decode()
            # Step 2: Constructing Regular Expressions
            # The regex patterns capture the values
            value_regex = re.compile(fr'{self.telegraf_fieldname}=([\d.]+)')
            light_regex = re.compile(r'light_mean=(\d)')

            # Step 3: Applying Regular Expressions
            value_match = value_regex.search(decoded_str)
            light_match = light_regex.search(decoded_str)

            # Ensure the regex found matches before attempting to access groups
            if value_match and light_match:
                # Step 4: Converting the Values
                value = float(value_match.group(1))
                light_on = int(light_match.group(1))  # This will be 1 or 0 as per the regex pattern
            self.logger.debug(f"Value: {value} Light On: {light_on}")
            if light_on:
                self.adjust_PID(value)



    def adjust_PID(self, value):

        seconds_on = self.pid.calc_secs_on(value)
        if seconds_on > 0.0:
            self.turn_on_power(seconds_on)


    def turn_on_power(self, seconds_on: float) -> None:
        """
        Turn on MistBuddy for a specified duration.

        Args:
            seconds_on (float): Duration to turn on MistBuddy in seconds.
        """
        # I was challenged because the power would be turned on but not off.  This got me to think there
        # was something wrong with threading.  But then I noticed the tasmotized devices were occassionally
        # not able to see Gus.  I had gotten a new wifi mesh and it doesn't seem to handle local ip names well.
        # gus.local was working until it is not.... so I had to hard code the ip address.  Yuk.

        # Set up a timer with the callback on completion.
        self.mqtt_client.start()
#        timer = threading.Timer(seconds_on, self.turn_off_power)
        # Start the client here, then stop in turn_off_mistbuddy
        self.logger.debug(f"POWER ON FOR {seconds_on} SECONDS")
        self._publish_power_plug_messages(seconds_on)
        self.mqtt_client.stop()
#        timer.start()

   # def turn_off_power(self) -> None:
   #     self.mqtt_client.start()
   #     self._publish_power_plug_messages(0)
   #     self.mqtt_client.stop()
   #     self.logger.debug("POWER OFF")

    def _publish_power_plug_messages(self, seconds_on: float) -> None:
        """
        Publish MQTT messages to control the power state.

        Args:
            power_state (int): Desired power state, either 1 (for on) or 0.
        """
        for power_command in self.mqtt_power_topics:
            self.mqtt_client.publish(power_command,1, qos=1)
            # Split the topic by the '/'
            parts = power_command.split('/')
            # Replace the last part with 'PulseTime'
            parts[-1] = "PulseTime"
            # Join the parts back together to form the new topic
            pulsetime_command = '/'.join(parts)
            pulsetime_on = seconds_on * 10
            self.mqtt_client.publish(pulsetime_command,pulsetime_on, qos=1)
            self.logger.debug(f"Topic {power_command} was turned on for {seconds_on} seconds.")


    def _handle_tuning(self,value: float) -> None:
        data_dict = {"Kp": value, "name": self.name}
        json_data = json.dumps(data_dict)
        # Convert the JSON string to bytes (required for sending over UDP)
        json_data_bytes = json_data.encode('utf-8')
        self.sock.sendto(json_data_bytes, self.address)
        self.logger.debug(f"-> wrote value {value} to address {self.address}")

