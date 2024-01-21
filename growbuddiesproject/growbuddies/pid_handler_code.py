#############################################################################
# SPDX-FileCopyrightText: 2024 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
from PID_code import PID_Control
from logginghandler import LoggingHandler
from mqtt_code import MQTTClient
from settings_code import Settings
import re
import socket
import threading


class PIDHandler:
    def __init__(self) -> None:
        """
        Initializes the PIDHandler with configurations loaded from growbuddies_settings.json. The focus is on the pid_configs section of growbuddies_settings.  There are pid configurations for each grow tent/location.

        The method sets up logging, loads the configuration settings, and initializes the PID controllers and associated threads based on the active configurations. A configuration is determined to be active if the active key within the dictionary for a particular config is true.

        Raises:
            RuntimeError: If there is an error loading the configuration settings.
        """

        self.logger = LoggingHandler()
        self.mqtt_client = MQTTClient()
        self.mqtt_client.start()
        try:
            settings = Settings()
            self.config = settings.load()
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            raise RuntimeError(f"Error loading settings: {e}")
        # Validate that essential configurations are present
        if "global_settings" not in self.config or "pid_configs" not in self.config:
            raise RuntimeError("Essential configuration sections missing")
        callback = None
        self.tune_increment = self.config

        self.incoming_udp_port = self.config["global_settings"].get("pid_port", 8095)
        self.pid_controllers_dict = {}  # Store pid controller instances key by location.
        self.pid_threads = []  # Each pid controller has its own thread.
        # Loop through each location's configurations
        for location, configs in self.config["pid_configs"].items():
            # Loop through each PID config within the tent
            for config_name, pid_config in configs.items():
                # Check if the PID config is active
                if pid_config.get("active", False):
                    if pid_config.get("tune_increment", 0) > 0:
                        self.tune_udp_port = self.config["global_settings"].get(
                            "tune_port", 8096
                        )
                        callback = self._public_Ku
                    else:
                        callback = None
                    controller = PID_Control(pid_config, callback)
                    value_name = pid_config.get("telegraf_fieldname")
                    unique_pid_controller_name = location + "-" + value_name
                    self.pid_controllers_dict[unique_pid_controller_name] = {
                        "controller": controller,
                        "value_name": value_name,
                        "mqtt_topics": pid_config.get("mqtt_power_topics"),
                    }
                    self.logger.info(
                        f"Setting up PID controller for {unique_pid_controller_name}"
                    )

                else:
                    self.logger.info(
                        f"PID controller for {location} with config: {config_name} is inactive"
                    )

    def start(self):
        """
        Starts the PID handling process by initiating a separate thread to manage the PID controller.

        This method creates a new thread targeting the listen_for_packets method. The thread
        is set as non-daemon to ensure it runs continuously in the background for the lifetime of the application.

        Raises:
            RuntimeError: If there is an error in creating or starting the thread.
        """
        try:
            thread = threading.Thread(target=self.listen_for_packets)
            thread.daemon = False
            thread.start()
        except Exception as e:
            self.logger.error(f"Failed to start PID handling thread: {e}")
            raise RuntimeError(f"Error starting PID handling thread: {e}")

    def listen_for_packets(self):
        """
        There is an aggregator set up in Telegraf that provides the average value after a time period of vpd and co2 based on the location of the snifferbuddy.  Telegraf sends the average values it calculated over the udp port identified in the "global_settings" section of growbuddies_settings.json as the 'pid_port' key.

        This method continuously listens for these incoming UDP packets and dispatches them to the appropriate PID controller.

        Raises:
            RuntimeError: If there is an error setting up or binding the UDP socket.
        """
        host = "127.0.0.1"
        try:
            values_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            values_socket.bind((host, self.incoming_udp_port))
            self.logger.debug(f" Listening on port {self.incoming_udp_port}")
        except Exception as e:
            self.logger.error(f"Failed to set up or bind UDP socket: {e}")
            raise RuntimeError(f"Socket setup/bind error: {e}")
        while True:
            try:
                packet = values_socket.recv(1024)
            except Exception as e:
                self.logger.error(f"Error receiving UDP packet: {e}")
                continue
            # Step 1: Decode the bytes
            decoded_str = packet.decode()
            # Packets include the location attribute (e.g.: tent one, tent two)
            location_match = re.search(r"location=([^,]+)", decoded_str)
            if location_match:
                location = location_match.group(1)
                # Dispatch to the correct PID controller based on location
                for key in self.pid_controllers_dict:
                    key_location, _ = key.split("-", 1)
                    if key_location == location:
                        controller = self.pid_controllers_dict[key]["controller"]
                        value_name = self.pid_controllers_dict[key]["value_name"]
                        mqtt_topics = self.pid_controllers_dict[key]["mqtt_topics"]
                        self.dispatch_to_controller(
                            controller, value_name, mqtt_topics, decoded_str
                        )
                    else:
                        self.logger.error(
                            f"No PID controller found for location: {location}"
                        )

    def dispatch_to_controller(self, controller, value_name, mqtt_topics, decoded_str):
        """
        Dispatches the incoming data to the specified PID controller based on the value name.

        This method parses the decoded string to extract relevant values using regular expressions and then
        calls the adjust_PID method to calculate and adjust the control as necessary.

        Args:
            controller (PID_Control): The PID controller instance to which the data is dispatched.
            value_name (str): The name of the value field to look for in the decoded string.
            decoded_str (str): The incoming data string to be parsed for values.

        Raises:
            ValueError: If the required values are not found in the decoded string.
        """
        try:
            value_regex = re.compile(rf"{value_name}=([\d.]+)")
            light_regex = re.compile(r"light_mean=(\d)")
            location_regex = re.compile(r"location=([^,]+)")
            # Step 3: Applying Regular Expressions
            value_match = value_regex.search(decoded_str)
            light_match = light_regex.search(decoded_str)
            location_match = location_regex.search(decoded_str)
            if not (value_match and light_match and location_match):
                raise ValueError("Required values not found in the incoming packet.")
            value = float(value_match.group(1))
            light_on = int(
                light_match.group(1)
            )  # This will be 1 or 0 as per the regex pattern
            location = location_match.group(1)
            self.logger.debug(
                f"Location: {location} Value: {value} Light On: {light_on}"
            )
            if light_on:
                self.adjust_PID(value, controller, mqtt_topics)
        except ValueError as e:
            self.logger.error(f"Dispatch error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in dispatch_to_controller: {e}")

    def adjust_PID(self, value, controller, mqtt_topics):
        """
        Adjusts the PID controller based on the provided value.

        This method calculates the control action using the PID controller's calc_secs_on method
        and then acts on the control output (e.g., turns on power to the actuators) if necessary.

        Args:
            value (float): The input value to the PID controller.
            controller (PID_Control): The PID controller instance to be adjusted.

        Raises:
            RuntimeError: If there is an error in calculating the PID output.
        """
        try:
            seconds_on = controller.calc_secs_on(value)
            if seconds_on > 0.0:
                self.turn_on_power(seconds_on, mqtt_topics)
        except Exception as e:
            self.logger.error(f"Error adjusting PID: {e}")
            raise RuntimeError(f"PID adjustment error: {e}")

    def turn_on_power(self, seconds_on: float, mqtt_topics) -> None:
        """
        Sends MQTT messages to turn on the power of the Tasmotized plugs used for MistBuddy and CO2Buddy for a specified duration.

        Args:
            seconds_on (float): The duration, in seconds, for which the power should be turned on.

        Raises:
            CommunicationError: If there is a failure in sending control commands.
            RuntimeError: If there is any other unexpected error.
        """
        # I was challenged because the power would be turned on but not off.  This got me to think there
        # was something wrong with threading.  But then I noticed the tasmotized devices were occassionally
        # not able to see Gus.  I had gotten a new wifi mesh and it doesn't seem to handle local ip names well.
        # gus.local was working until it is not.... so I had to hard code the ip address.  Yuk.

        # Set up a timer with the callback on completion.
        try:
            self.logger.debug(f"POWER ON FOR {seconds_on} SECONDS")
            self._publish_power_plug_messages(seconds_on, mqtt_topics)
        except Exception as e:
            self.logger.error(f"Unexpected error in turn_on_power: {e}")
            raise RuntimeError(f"Unexpected error: {e}")

    #        timer.start()

    # def turn_off_power(self) -> None:
    #     self.mqtt_client.start()
    #     self._publish_power_plug_messages(0)
    #     self.mqtt_client.stop()
    #     self.logger.debug("POWER OFF")

    def cleanup(self):
        """
        Cleans up the resources used by PIDHandler.

        This method stops the MQTT client, waits for all PID controller threads to complete, and ensures
        that all resources are properly released. It should be called before terminating the application
        or when the PIDHandler is no longer needed.
        """
        # Stopping the MQTT client
        self.mqtt_client.stop()
        self.logger.debug("MQTT client stopped.")

        # Joining all non-daemon threads to ensure they complete before exiting
        for thread in self.pid_threads:
            if thread.is_alive():
                self.logger.debug(f"Waiting for thread {thread.name} to complete.")
                thread.join()

        # Additional cleanup actions can be added here
        self.logger.debug("All threads have been terminated. Cleanup complete.")

    def _publish_power_plug_messages(self, seconds_on: float, mqtt_topics) -> None:
        """
        Publish MQTT messages to control the power state. The method uses Tasmota's PulseTime command as a timer amount for how long to keep the power plug on.  For a quick timer, set the PulseTime between 1 and 111.  Each number represents 0.1 seconds.  If the PulseTime is set to 10, the power plug stays on for 1 second.  Longer times use setting values between 112 to 649000.  PulseTime 113 means 13 seconds: 113 - 100. PulseTime 460 = 460-100 = 360 seconds = 6 minutes.

        Args:
            power_state (int): Desired power state, either 1 (for on) or 0.
        """
        for power_command in mqtt_topics:
            self.mqtt_client.publish(power_command, 1, qos=1)
            # Split the topic by the '/'
            parts = power_command.split("/")
            # Replace the last part with 'PulseTime'
            parts[-1] = "PulseTime"
            # Join the parts back together to form the new topic
            pulsetime_command = "/".join(parts)
            # We will use numbers between 112 and 64900 for the PulseTime (e.g.: 112 - 100 = 12 seconds)
            pulsetime_on = seconds_on + 100
            self.logger.debug(
                f"PulseTime: {pulsetime_on} Number seconds on: {pulsetime_on - 100}"
            )
            self.mqtt_client.publish(pulsetime_command, pulsetime_on, qos=1)
            self.logger.debug(
                f"Topic {power_command} was turned on for {seconds_on} seconds."
            )

    def _public_Ku(self, Ku):
        # Put the value into inline Influxdb format for Telegraf to pick up.
        influxdb_line = f"Ku_values Ku={Ku}"
        # Open the tuning socket.
        Ku_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            Ku_socket.sendto(influxdb_line.encode(), ("localhost", self.tune_udp_port))
        except socket.error as e:
            self.logger.error(f"Error sending tuning data to InfluxDB: {e}")
        finally:
            Ku_socket.close()
        return
