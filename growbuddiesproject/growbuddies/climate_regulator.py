#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################

from growbuddies.PID_code import PID
from growbuddies.logginghandler import LoggingHandler
from growbuddies.settings_code import Settings
from growbuddies.mqtt_code import MQTTClient
import threading
import time
from collections import deque



COMPARISON_FUNCTIONS = {
    "greater_than": lambda x, max_val: x > max_val,
    "less_than": lambda x, max_val: x <= max_val,
}

class ClimateRegulator:
    def __init__(self, pid_dict_key):

        self.logger = LoggingHandler()
        settings = Settings()
        settings.load()
        pid_dict = settings.get(pid_dict_key)
        self.update_interval = pid_dict.get("update_interval", 20)
        self.stop_thread = False
        self.device_deques = {}
        self.rolling_window_size = settings.get('rolling_window_size',3)
        self.average_value = None
        self.comparison_func_name = pid_dict["comparison_function"]
        self.comparison_func = COMPARISON_FUNCTIONS.get(
                self.comparison_func_name
            )

        self.setpoint = pid_dict["setpoint"]
        self.mqtt_topics = pid_dict["mqtt"]
        self._light_on = None
        self.timer = None
        # We use the mqtt client to send power on and off messages to the mistbuddy plugs.
        self.mqtt_client = MQTTClient("ClimateRegulator")
        self.pid = PID(pid_dict)

    @property
    def light_on(self):
        return self._light_on

    @light_on.setter
    def light_on(self, status):
        self._light_on = bool(status)  # Convert to boolean
        self.logger.debug(f"Light status set to: {status}")

    def start(self):
        self.stop_thread = False
        self.adjust_control_thread = threading.Thread(target=self.periodic_adjustment)
        self.adjust_control_thread.start()

    def add_value_to_window(self, name, value):
        if name not in self.device_deques:
            self.device_deques[name] = deque(maxlen=self.rolling_window_size)
        self.device_deques[name].append(value)
        # Check if all deques have at least running_window_size values and the same length
        lengths = [len(deq) for deq in self.device_deques.values()]
        ready_for_pid = False
        if len(set(lengths)) == 1 and lengths[0] >= self.rolling_window_size:
                    # Calculate the average across all deques
            ready_for_pid = True
            all_values = [val for deq in self.device_deques.values() for val in deq]
            self.average_value = sum(all_values) / len(all_values)
        self.logger.debug(f"Updating average. Value: {value}.  Average: {self.average_value}")
        return ready_for_pid

    def periodic_adjustment(self):
        self.logger.debug("PERIODIC ADJUSTMENT.")
        while not self.stop_thread:
            if self.average_value is not None and self.light_on:
                self.adjust_control(self.average_value)
            time.sleep(self.update_interval)

    def adjust_control(self, value):
        seconds_on = self.pid.calc_secs_on(value)
        # Insert custom logic for control here
        self.logger.debug(f"--> ADJUST_CONTROL. value: {value}, setpoint: {self.setpoint}")
        if self.comparison_func(value, self.setpoint):
            # Either too high (CO2) or too low (vpd)
            self.turn_off_power()
            comparison_word = "higher" if self.comparison_func_name == "greater_than" else "lower"
            self.logger.debug(f"The value mean: {value} is {comparison_word} than it should be.")
        elif self.comparison_func(self.setpoint, value):
            if seconds_on > 0.0:
                self.turn_on_power(seconds_on)
                self.logger.debug(f"seconds on: {seconds_on} average value: {value}")

    def turn_on_power(self, seconds_on):
        self.mqtt_client.start()
        self.timer = threading.Timer(seconds_on, self.turn_off_power)
        for topic in self.mqtt_topics:
            self.mqtt_client.publish(topic, 1)
        self.mqtt_client.stop()
        self.logger.debug("CONTROL START!")
        self.timer.start()


    def turn_off_power(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None
        self.mqtt_client.start()
        for topic in self.mqtt_topics:
            self.mqtt_client.publish(topic, 0)
        self.mqtt_client.stop()
        self.logger.debug("CONTROL OFF!")


    def stop(self):
        self.stop_thread = True
        if self.adjust_control_thread.is_alive():
            self.adjust_control_thread.join()
