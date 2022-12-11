from growbuddies.PID_code import PID
import logging
from enum import Enum
from growbuddies.gus import Gus
from growbuddies.snifferbuddyreadings import SnifferBuddyReadings
import threading
import signal


class growthStage(Enum):
    """An enumeration to let growBuddy know if the plants it is caring for are in the vegetative or flower growth stage.

       Args:

            Enum (int): Either VEG for Vegetative of FLOWER for when the plant is in flowering.

    """

    VEG = 2
    FLOWER = 3


class MistBuddy(Gus):

    """Keeps the humidity at the ideal VPD level.  If we get this right, it should run just by initiating an instance
    of this class.  We set a values_callback if we want to get to the data. For example, if we wish to store the
    data into influxdb.

    Args:
        vpd_values_callback (function, optional): Callback to get all the readings. Defaults to None.

        growth_stage (growthStage Enum, optional): Whether the plant is in vegetative or is flowering. Defaults to growthStage.VEG.

        manage (bool, optional): Whether the caller wishes to just observe values or wants vpdBuddy to start turning mistBuddy ON
            and OFF. Defaults to True.

    Raises:
        Exception: Code checks if the vpd setpoint it reads from the settings file is within expected values.  If it isn't, an exception
            is raised.

    """

    def __init__(
        self,
        vpd_values_callback=None,
        snifferbuddy_status_callback=None,
        growth_stage=growthStage.VEG,
        readings_table_name=None,
        manage=True,
    ):
        # Set up for a Systemd stop command by setting up a SIGTERM handler
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        # MistBuddy uses Gus to get SnifferBuddy values.s
        super().__init__(SnifferBuddyReadings_callback=self._values_callback, SnifferBuddyReadings_table_name=readings_table_name,
                         status_callback=snifferbuddy_status_callback, log_level=logging.DEBUG)
        self.vpd_values_callback = vpd_values_callback
        self.manage = manage
        msg = (
            "Managing vpd."
            if self.manage
            else "Observing vpd."
        )
        self.logger.debug(msg)
        # Checking if the light changed from off to on.  If it did, the PID controller should know this so it can reset the error part
        # that accumulates.
        self.prev_light_on_or_off = None
        # Set up the setpoint to the ideal vpd value.
        self.setpoint = 0.0
        if growth_stage == growthStage.VEG:
            self.setpoint = self.settings["vpd_setpoints"]["veg"]
        else:
            self.setpoint = self.settings["vpd_setpoints"]["flower"]
        # The setpoint should be around .6 to 1.6...
        if not isinstance(self.setpoint, float) or self.setpoint * 10 not in range(20):
            raise Exception(
                "The vpd setpoint should be a floating point number between 0.0 and less than 2.0"
            )
        # These are used in the _pid() routine.
        self.pid_cum_error = 0.0
        self.pid_last_error = 0.0
        # Initialize the PID tuning variables.
        # How far away from the destination - Proportional
        Kp = self.settings["PID_settings"]["Kp"]
        Ki = self.settings["PID_settings"]["Ki"]
        Kd = self.settings["PID_settings"]["Kd"]
        # By default mqtt_time is used for time between sampling.
        clamp = (self.settings["PID_settings"]["output_limits"][0], self.settings["PID_settings"]["output_limits"][1])
        self.pid = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=self.setpoint, output_limits=(clamp))
        # The PID class as a __repr__() method.
        self.logger.debug(self.pid)

    def _has_light_just_turned_on(self):
        if self.prev_light_on_or_off is None or not self.prev_light_on_or_off:
            self.logger.debug("The grow lights just turned on.")
            return True
        # if the values are the same, return False indicating no change

        return False

    def _values_callback(self, s: SnifferBuddyReadings):
        """growBuddy calls this method when it receives a reading from the requested sensor. vpd adjustment occurs during
        transpiration.  Transpiration is occuring when the grow lights are on.  The vpd will not be adjusted when the grow
        lights are off.

        Args:
            s (SnifferBuddyReadings): A reading from SnifferBuddy within an instance of SnifferBuddyReadings.
        """
        if s.light_level > 700:  # A light strong enough to start transpiration is assumed if the photoresister is between 700 and 1024.
            nSecondsON, error = self._pid(s.vpd, self._has_light_just_turned_on())
            self.prev_light_on_or_off = True
            self.logger.debug(
                f"vpd: {s.vpd}   num seconds to turn humidifier on: {nSecondsON}. "
            )
            if self.manage and nSecondsON > 0:
                self._turn_on_mistBuddy(nSecondsON)

        else:
            self.logger.debug(f"The grow lights are OFF. No vpd adjustment.  The Light Level is {s.light_level} ")
            self.prev_light_on_or_off = False
        if self.vpd_values_callback:
            self.vpd_values_callback(self.setpoint, s.vpd, nSecondsON, error)

    def _pid(self, reading: float, light_just_turned_on: bool) -> int:
        """This is the code for the PID controller.

        Args:
            reading (float): The vpd value that will be compared to the setpoint.

        Returns:
            int: The number of seconds to turn on mistBuddy.

        The goals of this PID controller are:

        * Automatically adjust the humidity within a grow tent to the vpd setpoint.

        * Be better than a "BANG-BANG" controller by not constantly turning mistBuddy on and off.


        More like **This**

        .. image:: ../docs/images/PID_controller.jpg
            :scale: 35
            :alt: PID Controller
            :align: center

        Than **This**

        .. image:: ../docs/images/bangbang_controller.jpg
            :scale: 30
            :alt: BANG BANG Controller
            :align: center

        .. note::
            I expect this method to evolve over time.

            - I am new to PID controllers.  I'm bumbling about tuning it.  My goal is to get advice from folks that know more than me,
              and then improve the code.

            - I am optimizing for my environment - a climate controlled area with a grow tent.  The temperature is in the 70's F.  The relative
              humidity is typically around 40-50%.
        """

        nSecondsOn, error = self.pid(reading, light_just_turned_on)
        return nSecondsOn, error

    def _turn_on_mistBuddy(self, nSecondsON: int) -> None:
        """Send mqtt messages to mistBuddy's plugs to turn ON.

        Args:
            nSecondsON (int): The number of seconds to turn the plugs on.

        """
        # Set up a timer with the callback on completion.
        timer = threading.Timer(nSecondsON, self._turn_off_mistBuddy)
        # The command to a Sonoff plug can be either TOGGLE, ON, OFF.
        # Send the command to power ON.
        self.mqtt_client.publish(self.settings["mqtt"]["mistBuddy_fan_topic"], "ON")
        self.mqtt_client.publish(self.settings["mqtt"]["mistBuddy_mister_topic"], "ON")
        self.logger.debug(
            f"...Sent mqtt messages to the two mistBuddy plugs to turn ON for {nSecondsON} seconds."
        )
        timer.start()

    def _turn_off_mistBuddy(self):
        """The timer set in _turn_on_mistBuddy has expired.  Send messages to the
        mistBuddy plugs to turn OFF."""

        self.mqtt_client.publish(self.settings["mqtt"]["mistBuddy_fan_topic"], "OFF")
        self.mqtt_client.publish(self.settings["mqtt"]["mistBuddy_mister_topic"], "OFF")
        self.logger.debug(
            "...Sent mqtt messages to the two mistBuddy plugs to turn OFF."
        )

    def _exit_gracefully(self):
        self._turn_off_mistBuddy(self)
        exit(0)
