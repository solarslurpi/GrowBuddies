
import logging
from enum import Enum
from growbuddy_code import GrowBuddy
import threading

settings_filename = "code/growbuddy_settings.json"


class growthStage(Enum):
    """An enumeration to set the stage of plant growth.  Whether in vegetative or flower is an input from the user.
    The code then converts this to a growthStage enum and passes the value when instantiating an instance of the
    VPDcontroller() class.

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
        snifferbuddy_values_callback (function, optional): Callback to get all the readings. Defaults to None.
        growth_stage (_type_, optional): Whether the plant is in vegetative or is flowering. Defaults to growthStage.VEG.

    Raises:
        Exception: There are a few exception states to check and can alert the caller.
    """

    def __init__(
        self,
        snifferbuddy_values_callback=None,
        growth_stage=growthStage.VEG,
        manage=False,
    ):
        super().__init__(values_callback=self._values_callback, log_level=logging.DEBUG)
        self.snifferbuddy_values_callback = snifferbuddy_values_callback
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
            self.setpoint = self.settings["veg_setpoint"]
        else:
            self.setpoint = self.settings["flower_setpoint"]
        # The setpoint should be around .6 to 1.6...
        if not isinstance(self.setpoint, float) or self.setpoint * 10 not in range(20):
            raise Exception(
                "The vpd setpoint should be a floating point number between 0.0 and 2.0"
            )
        self.logger.debug(f"The value for the vpd setpoint is: {self.setpoint}")
        # These are used in the _pid() routine.
        self.pid_cum_error = 0.0
        self.pid_last_error = 0.0

    def _values_callback(self, dict):
        """GrowBuddy calls this method when it receives a reading from the requested sensor.

        Args:
            dict (Dictionary): For example, a SnifferBuddy dict looks something like:
            {"Time":"2022-09-06T08:52:59",
            "ANALOG":{"A0":542},
            "SCD30":{"CarbonDioxide":814,"eCO2":787,"Temperature":71.8,"Humidity":61.6,"DewPoint":57.9},"TempUnit":"F"}
        """

        self.logger.debug(f"vpdControler's values_callback. Dict:{dict}")
        vpd = self._calc_vpd(dict)
        nSecondsON = self._pid(self.setpoint, vpd)
        self.logger.debug(
            f"vpd: {vpd}   num seconds to turn humidifier on: {nSecondsON}"
        )
        if self.manage and nSecondsON > 0:
            self._turn_on_vaporBuddy(nSecondsON)

        if self.snifferbuddy_values_callback:
            # sniffer_dict = self._make_sniffer_dict(time, air_T, RH, vpd, nSecondsON, dict['ANALOG']['A0'])
            dict["vpd_setpoint"] = self.setpoint
            dict["vpd"] = vpd
            dict["seconds_on"] = nSecondsON
            self.snifferbuddy_values_callback(dict)

    def _pid(self, setpoint: float, reading: float) -> int:
        """INTERNAL METHOD.  This is the code for the `PID controller <https://en.wikipedia.org/wiki/PID_controller>`_

        The PID controller is at the heart of determining how many seconds to turn on the humidifier.  I expect this
        method to be evolved over time.
        1. I am optimizing for my environment - a climate controlled area with a grow tent.  The temperature is in the
        70's F.  The relative humidity is typically around 40-50%.
        2. I am new to PID controllers.  I have to start somewhere, but I am quite sure I will cringe at this code
        a year from now!

        Args:
            setpoint (float): The ideal value for the VPD.
            reading (float):  The most recent reading.

        Returns:
            int: How many seconds to turn on the humidifier on.
        """
        Kp = self.settings["Kp"]
        Ki = self.settings["Ki"]
        Kd = self.settings["Kd"]
        # This code is designed for my setup.  The indoors is climate cocntrolled.  There is only a humidifier to turn
        # on or off - that is, it is always the case more humidity is needed and
        # the air temperature is a comfortable range for the plants.
        # If setpoint - reading is positive, the air in the grow room is too humid.  Most (pretty much all?)
        # of the time the error should be negative.
        error = setpoint - reading
        if error > 0.0:
            return 0
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
            f"pCorrection is {pCorrection}, iCorrection is {iCorrection}, dCorrection is {dCorrection}"
        )
        # Calculate the # Seconds to turn Humidifier on.  I am roughly guessing 1 second on lowers VPD by .01.
        # A Wild Guess to be sure.
        nSecondsON = abs(int((pCorrection + iCorrection + dCorrection) * 100))
        # Tapping off the max number of seconds VaporBuddy can be on
        nSecondsON = nSecondsON if nSecondsON < 10 else 10
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
