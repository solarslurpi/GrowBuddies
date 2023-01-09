"""SnapBuddy is the Buddy you want to take a timelapse of your plant.  The SnapBuddy device has
the ESP32-CAM Tasmota with the AI Thinker Template installed.
"""
import sys


sys.path.insert(0, "../")

from growbuddies.settings_code import Settings
import requests
import datetime
import time
import os
from growbuddies.logginghandler import LoggingHandler


class SnapBuddy:
    def __init__(self, settings_string=None):
        self.logger = LoggingHandler()
        if settings_string is None:
            self.logger.error(
                "An empty string was provided as an input for a valid entry in the growbuddies_settings for a snapbuddy. "
                " Please provide a valid string representing an entry in the growbuddies_settings for the snapbuddy."
            )
            sys.exit()
        settings = Settings()
        settings.load()
        self.snapbuddy_settings_dict = settings.get(settings_string)
        self.settings_string = settings_string  # For __repr__ documentation.

        if self.snapbuddy_settings_dict is None:
            self.logger.error(
                f"The settings_string '{settings_string}' was not found in the growbuddies_settings. "
                "Please provide a valid string representing an entry in the growbuddies_settings for the snapbuddy."
            )
            sys.exit()
        try:
            self.hostname = self.snapbuddy_settings_dict["hostname"]
            self._interval_secs = self.snapbuddy_settings_dict["interval_secs"]
            self.timelapse_dir = self.snapbuddy_settings_dict["timelapse_dir"]
        except KeyError as e:
            self.logger.error(
                f"The settings_string '{settings_string}' was found in the growbuddies_settings but the key '{e}' was not found. "
                "Please provide a valid {e} : value pair in the growbuddies_settings for the snapbuddy"
            )
            sys.exit()

    def __repr__(self):
        return (
            f"SnapBuddy(settings_string='{self.settings_string}', "
            f"hostname='{self.hostname}', "
            f"interval_secs={self.interval_secs}, "
            f"timelapse_dir='{self.timelapse_dir}')"
        )

    def snap(self):
        # This is the URL to get a snapshot from a Tasmota running
        # an ESP32-CAM with the AI Thinker template installed.
        url = "http://" + self.hostname + ":80/snapshot.jpg"
        # Send the request to the Tasmota device to capture a snapshot
        response = requests.get(url)

        if response.status_code == 200:
            filename = self._get_filename()

            # Save the snapshot image to a file
            with open(filename, "wb") as f:
                f.write(response.content)
            self.logger.debug(f"Snapshot saved to {filename}")
        else:
            self.logger.error(
                f"Could not get the snapshot from {self.hostname}. The response code was {response.status_code} and the reason was {response.reason}."
            )

        # Check if the request was successful
        self.logger.debug(f"response code: {response.status_code}")

    @property
    def interval_secs(self):
        return self._interval_secs

    def _get_filename(self):
        """Get the filename for the snapshot image.
        The filename is a combination of the timelapse directory and the current date and time.
        """
        # Make sure the timelapse directory exists
        # Split the file path into individual directories
        dirs = self.timelapse_dir.split("/")
        # remove the root directory
        dirs.pop(0)

        # Iterate through the directories, creating each one if it does not exist
        subdir = ""
        for i in range(len(dirs)):
            subdir += "/" + dirs[i]
            if not os.path.exists(subdir):
                os.mkdir(subdir)
        filename = f"{self.timelapse_dir}/{datetime.datetime.now().strftime('%m%d%Y_%H%M%S')}.jpg"
        return filename


def main():
    logger = LoggingHandler()

    snapbuddy = SnapBuddy("snapbuddy_settings_1")
    logger.debug(f"-> SnapBuddy class initialized. {snapbuddy}")
    while True:
        try:
            snapbuddy.snap()
        except KeyboardInterrupt:
            sys.exit()

        time.sleep(snapbuddy.interval_secs)


if __name__ == "__main__":
    main()
