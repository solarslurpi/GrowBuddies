#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
from typing import Optional, Tuple, Union
from logginghandler import LoggingHandler
from mqtt_code import MQTTService
from snifferbuddyreadings_code import SnifferBuddyReadings
from settings_code import Settings
import sys
import queue


class SnifferBuddyHandler:
    """
    This class makes it easy for the user to start receiving readings and status messages from SnifferBuddy.  The messages are queued, from which the user retrieves them.

    Settings from the :ref:`GrowBuddies Settings <_growbuddies_settings>` file are used to communicate with the MQTT broker.  The settings include:

    - the **hostname** of the Raspberry Pi Server (Usually Gus).  This setting is used within the MQTTClient class to direct the IP traffic to the right MQTT broker.
    - the **MQTT Topics and callbacks**. NOTE: If the user wants to change the topic's callback names, they will have to change the method names within this class.
    """

    def __init__(self):
        """
        Initialize the SnifferBuddyHandler with a new message queue and a logging handler.
        """
        self.message_queue = queue.Queue()
        self.logger = LoggingHandler()

    def on_snifferbuddy_readings(self, mqtt_payload: str) -> None:
        """
        Callback for when a SnifferBuddy reading message is received.

        This message parses the MQTT payload into a SnifferBuddyReadings object and puts the
        readings into the message queue.

        Args:
            mqtt_payload (str): The MQTT payload containing the SnifferBuddy readings.
        """
        s = SnifferBuddyReadings(mqtt_payload)
        if s.valid_packet:
            # self.logger.info(f'---> INITIAL VPD: {s.dict["vpd"]}')
            # self.logger.debug(f"SnifferBuddy Readings after a conversion from msg.payload {s.dict}")
            self.message_queue.put(("readings", s.dict))

    def on_snifferbuddy_status(self, status: str) -> None:
        """
        Callback for when a SnifferBuddy status (lwt) message is received.

        This method puts the status into the message queue.

        Args:
            status (str): The status message received from the SnifferBuddy system.
        """
        self.logger.debug(f"-> SnifferBuddy is: {status}")
        self.message_queue.put(("status", status))

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
        methods = settings.get_callbacks("snifferbuddy_mqtt", self)
        self._mqtt_service = MQTTService(methods)
        self._mqtt_service.start()

    def stop(self):
        self._mqtt_service.stop()
        sys.exit()

    @property
    def mqtt_service(self):
        return self._mqtt_service
