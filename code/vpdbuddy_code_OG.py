
import logging
from enum import Enum
from growbuddy_code import GrowBuddy
import threading
from snifferbuddy_code import snifferBuddy

settings_filename = "code/growbuddy_settings.json"


class growthStage(Enum):
    """An enumeration to let GrowBuddy know if the plants it is caring for are in the vegetative or flower growth stage.

       Args:

            Enum (int): Either VEG for Vegetative of FLOWER for when the plant is in flowering.

    """

    VEG = 2
    FLOWER = 3


class vpdBuddy(GrowBuddy):

    """Keeps the humidity at the ideal VPD level.  If we get this right, it should run just by initiating an instance
    of this class.  We set a values_callback if we want to get to the data. For example, if we wish to store the
    data into influxdb.

    Args:
        vpd_values_callback (function, optional): Callback to get all the readings. Defaults to None.

        growth_stage (growthStage Enum, optional): Whether the plant is in vegetative or is flowering. Defaults to growthStage.VEG.

        manage (bool, optional): Whether the caller wishes to just observe values or wants vpdBuddy to start turning vaporBuddy ON
            and OFF. Defaults to False (only observe values by setting the svpd_values_callback).

    Raises:
        Exception: Code checks if the vpd setpoint it reads from the settings file is within expected values.  If it isn't, an exception
            is raised.

    """

    def __init__(
        self,
        vpd_values_callback=None,
        growth_stage=growthStage.VEG,
        snifferbuddy_table_name=None,
        manage=False,
    ):
        # vpdBuddy needs the snifferBuddy values.  This is why the growBuddy callback is set to
        # the internal _values_callback() method.
        super().__init__(growBuddy_values_callback=self._values_callback, snifferbuddy_table_name=snifferbuddy_table_name, log_level=logging.DEBUG)
        self.vpd_values_callback = vpd_values_callback
        self.manage = manage
        msg = (
            "Turning VaporBuddy Plugs ON and OFF"
            if self.manage
            else "Observing SnifferBuddy Readings"
        )
        self.logger.debug(msg)
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
        self.logger.debug(f"The value for the vpd setpoint is: {self.setpoint}")
        # These are used in the _pid() routine.
        self.pid_cum_error = 0.0
        self.pid_last_error = 0.0

    def _values_callback(self, s: snifferBuddy):
        """GrowBuddy calls this method when it receives a reading from the requested sensor.

        Args:
            vpd (float): The calculated vpd value from the most recent snifferBuddy reading.


        """
        nSecondsON = self._pid(self.setpoint, s.vpd)
        self.logger.debug(
            f"vpd: {s.vpd}   num seconds to turn humidifier on: {nSecondsON}"
        )
        if self.manage and nSecondsON > 0:
            self._turn_on_vaporBuddy(nSecondsON)

        if self.vpd_values_callback:
            self.vpd_values_callback(self.setpoint, s.vpd, nSecondsON)

    def _pid(self, setpoint: float, reading: float) -> int:
        """This is the code for the PID controller.

        Args:
            setpoint (float): The ideal vpd value.
            reading (float): The vpd value that will be compared to the setpoint.

        Returns:
            int: The number of seconds to turn on vaporBuddy.

        The goals of this PID controller are:

        * Automatically adjust the humidity within a grow tent to the vpd setpoint.

        * Be better than a "BANG-BANG" controller by not constantly turning vaporBuddy on and off.


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
        # How far away from the destination - Proportional
        Kp = self.settings["PID_settings"]["Kp"]

        Ki = self.settings["PID_settings"]["Ki"]

        Kd = self.settings["PID_settings"]["Kd"]
        nSecondsON = 0
        error = setpoint - reading
        # If the error is is > 0, it means the reading is too humid .  The current code adjust only when the error is negative - the area is too dry.
        if error > 0:
            return nSecondsON

        # Calculate the Proportional Correction
        pCorrection = Kp * error
        # Calculate the Integral Correction
        self.pid_cum_error += error
        iCorrection = Ki * self.pid_cum_error
        # Calculate the Derivitive Correction
        slope = error - self.pid_last_error
        dCorrection = Kd * slope
        self.pid_last_error = error
        self.logger.debug(
            f"error is {error}, pCorrection is {pCorrection}, iCorrection is {iCorrection}, dCorrection is {dCorrection}"
        )
        # Tuning to calculate the number of seconds to turn the humidifier on seems to take on a bit of a Wild Ass Guess.
        # Calculate the # Seconds to turn Humidifier on.  I am roughly guessing 1 second on lowers VPD by .01.
        # A Wild Guess to be sure.
        nSecondsON = abs(int((pCorrection + iCorrection + dCorrection) * 100))
        # Tapping off the max number of seconds VaporBuddy can be on
        # nSecondsON = nSecondsON if nSecondsON < 10 else 10
        self.logger.debug(
            f"Number of seconds to turn on the Humdifier is {nSecondsON}."
        )
        return nSecondsON

    def _turn_on_vaporBuddy(self, nSecondsON: int) -> None:
        """Send mqtt messages to vaporBuddy's plugs to turn ON.

        Args:
            nSecondsON (int): The number of seconds to turn the plugs on.

        """
        # Set up a timer with the callback on completion.
        timer = threading.Timer(nSecondsON, self._turn_off_vaporBuddy)
        # The command to a Sonoff plug can be either TOGGLE, ON, OFF.
        # Send the command to power ON.
        self.mqtt_client.publish(self.settings["mqtt_vaporbuddy_fan_topic"], "ON")
        self.mqtt_client.publish(self.settings["mqtt_vaporbuddy_mister_topic"], "ON")
        self.logger.debug(
            f"...Sent mqtt messages to the two vaporBuddy plugs to turn ON for {nSecondsON} seconds."
        )
        timer.start()

    def _turn_off_vaporBuddy(self):
        """The timer set in _turn_on_vaporBuddy has expired.  Send messages to the
        vaporBuddy plugs to turn OFF."""

        self.mqtt_client.publish(self.settings["mqtt_vaporbuddy_fan_topic"], "OFF")
        self.mqtt_client.publish(self.settings["mqtt_vaporbuddy_mister_topic"], "OFF")
        self.logger.debug(
            "...Sent mqtt messages to the two vaporBuddy plugs to turn OFF."
        )