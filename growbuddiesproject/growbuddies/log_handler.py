#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
from typing import Optional, Tuple, Union
from growbuddies.logginghandler import LoggingHandler
from growbuddies.mqtt_code import MQTTService
from growbuddies.settings_code import Settings
import sys
import queue
import time


class LogHandler:
    def __init__(self):
        self.message_queue = queue.Queue()
        self.logger = LoggingHandler()
        self.log_filename = None

    def on_debug_msg(self, mqtt_payload: str) -> None:
        self.logger.debug(f"DEBUG===> {mqtt_payload}")

    def on_error_msg(self, mqtt_payload: str) -> None:
        """
        Callback for when a SnifferBuddy status (lwt) message is received.

        This method puts the status into the message queue.

        Args:
            status (str): The status message received from the SnifferBuddy system.
        """
        self.logger.debug(f"DEBUG===> {mqtt_payload}")
        # self.message_queue.put(("status", status))

    def get_message_from_queue(self) -> Optional[Tuple[str, Union[str, dict]]]:
        """
        Retrieve the next message from the message queue, if one is available.

        This method checks if the message queue is not empty and, if it's not, returns the next message. If the queue is
        empty, it returns None.

        Returns:
            tuple: A tuple containing the type of the message ('reading' or 'status') and the content of the message.
            None: If the queue is empty.
        """
        if not self.message_queue.empty():
            return self.message_queue.get()
        return None

    def start(self):
        """
        Start the SnifferBuddyHandler.

        This method loads the settings, retrieves the callback methods and starts the MQTT service
        """
        settings = Settings()
        settings.load()
        methods = settings.get_callbacks("debug_mqtt", self)
        self.mqtt_service = MQTTService(methods)
        self.mqtt_service.start()

    def stop(self):
        self.mqtt_service.stop()
        sys.exit()


log_handler = LogHandler()
log_handler.start()
while True:
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        log_handler.stop()
