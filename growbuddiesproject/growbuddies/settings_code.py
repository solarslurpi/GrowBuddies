#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
import json
import os

settings_filename = "growbuddies_settings.json"


class Settings:
    def __init__(self):
        """Set the working directory to where the Python files are located."""
        cfd = os.path.dirname(os.path.realpath(__file__))
        os.chdir(cfd)
        # self.logger.debug(f"--> Current Directory is {os.getcwd()}")
        self.settings = {}

    def load(self) -> None:
        """Load the growbuddies_settings.json file.

        Raises:
            Exception: Returns a string letting the caller know the json file could not be opened.
        """
        try:
            with open(settings_filename) as json_file:
                self.settings = json.load(json_file)
        except Exception as e:
            raise Exception(
                f"Could not open the settings file named {settings_filename}.  Error: {e}"
            )

    def get(self, key, default=None) -> str:
        """The get() method is a convenient way to access the values stored in the growbuddies_settings.json file.
        It serves as a wrapper around the built-in get() method of dictionaries.  If a value does not exist for a key,
        but a default value is provided, the default value is returned.  If a value does not exist for a key and no default
        value is provided, an exception is raised.

        Args:
            key (str): One of the keys in the growbuddies_settings.json file.

            default (str, optional): A default value to return if the key does not exist. Defaults to None.

        Raises:
            Exception: Occurs if the key does not exist and no default value is provided. The exception message
            contains the key and the value.

        Returns:
            str: The value associated with the key.
        """
        value = self.settings.get(key)
        return value if value else default

    def get_callbacks(self, key: str, instance_of_callbacks_class) -> dict:
        """get_callbacks() returns a dictionary of callback methods to be called by the
        :py:meth:`growbuddies.mqtt_code.MQTTClient.on_message`. For example, the
        growbudies_settings.json file contains several callback dictionaries. Here is the
        callback dictionary for SnifferBuddy:

        .. code:: json

            {
            "snifferbuddy_mqtt": {
                "tele/snifferbuddy/SENSOR": "on_snifferbuddy_readings",
                "tele/snifferbuddy/LWT": "on_snifferbuddy_status"
                }
            }

        The dictionary states for the key "snifferBuddy_mqtt", when a message is received on the topic
        "tele/snifferbuddy/SENSOR", the method on_snifferbuddy_readings() is to be called.  When a
        message is received on the topic "tele/snifferbuddy/LWT", the method on_snifferbuddy_status() is to be called.

        Typically, this method is called prior to instantiating an instance of the
        :py:class:`growbuddies.mqtt_code.MQTTService` class. For example, the following code instantiates
        an instance of the MQTTService class and passes the callbacks dictionary to the MQTTService class:

        .. code-block:: python

            settings = Settings()
            settings.load()
            callbacks = Callbacks()
            methods = settings.get_callbacks("snifferbuddy_mqtt", callbacks)
            mqtt_service = MQTTService(methods)
            mqtt_service.start()

        Args:
            key (str): Key to the method names in the instance_to_callbacks_class instance that are to be called
            when a message is received on the topic associated with the key.  In the above example, the caller has
            written the two callback methods, :on_snifferbuddy_readings() and on_snifferbuddy_status().

            instance_to_callbacks_class (class instance): Instance of the class that contains the callback methods.

        Returns:
            dict (dict): A dictionary of callback methods to be called by :py:class:`growbuddies.mqtt_code.MQTTService`.
            The dictionary is keyed by the topic and the value is the callback method to be called.
        """
        callbacks_for_topic = self.get(key)
        callback_methods = {}
        for topic in callbacks_for_topic.keys():
            try:
                callback_methods[topic] = getattr(
                    instance_of_callbacks_class, callbacks_for_topic[topic]
                )
            except AttributeError:
                print(f"Just a FYI: No callback registered for topic {topic}.")
                callback_methods[topic] = None
        return callback_methods
