
import json
import math
import os
import logging
import threading

import paho.mqtt.client as mqtt
from logging_handler import LoggingHandler
from enum import Enum

settings_filename = 'growbuddy_settings.json'

class growthStage(Enum):
    """An enumeration to set the stage of plant growth.  Whether in vegetative of flower is an input from the user.  The code then converts this to a growthStage enum and passes the value when instantiating an instance of the VPDcontroller() class.

    Args:
        Enum (int): Either VEG for Vegetative of FLOWER for when the plant is in flowering.
    """
    VEG = 2
    FLOWER = 3

class VPDcontroller():

    """Keeps the humidity at the ideal VPD level.  If we get this right, it should run just by initiating an instance of this class.  We set a values_callback if we want to get to the data. For example, if we wish to store the data into influxdb.

    Args:
        growth_stage (class growthStage (which is an Enum), optional): Entered by the user. Defaults to growthStage.VEG.
        values_callback (function, optional): Function in the caller's code that is called back when there is data to pass back. Defaults to None.
        log_level (_type_, optional):Logging level.  DEBUG is useful while setting up.  Then switching to INFO is a great idea to cut back on the volume of log entries. Defaults to logging.DEBUG.

    Raises:
        Exception: There are a few exception states to check to make sure the code knows what is going on and can alert the caller.
    """

    def __init__(self, growth_stage: int = growthStage.VEG, values_callback = None, log_level = logging.DEBUG):

        # Used for initialization of PID controller when the first mqtt message from SnifferBuddy comes in.
        self.first_message = True
        self.values_callback = values_callback

        # Set up logging to go to the console.
        self.logger = LoggingHandler(log_level)
        self.logger.debug("-> Initializing VPDcontroller class")
        # Get settings out of JSON file.
        try:
            self.settings = self._read_settings()
            self.logger.debug(f'...Settings: {self.settings}')
        except Exception as e:
            self.logger.debug(f'...Exiting due to Error: {e}')
            os._exit(1)

 
        # Set up the setpoint to the ideal vpd value.ds
        self.setpoint = 0.0
        if growth_stage == growthStage.VEG:
            self.setpoint = self.settings['veg_setpoint']
        else:
            self.setpoint = self.settings['flower_setpoint']
        # The setpoint should be around .6 to 1.6...
        if not isinstance(self.setpoint,float) or self.setpoint*10 not in range(20):
            raise Exception ( "The vpd setpoint should be a floating point number between 0.0 and 2.0")
        self.logger.debug(f'The value for the vpd setpoint is: {self.setpoint}')
        # These are used in the _pid() routine.
        self.pid_cum_error = 0.0
        self.pid_last_error = 0.0

        # Connect up with mqtt.
        try:
            self.client = mqtt.Client('vpdBuddy')
            self.client.on_message = self._on_message
            self.client.on_connect = self._on_connect
            self.client.connect(self.settings['mqtt_broker'])
            # At this point, mqtt drives the code.
            self.logger.debug('VPDcontroller has been initialized.  Handing over to mqtt.')
            self.client.loop_forever()


        except Exception as e:
            self.logger.debug(f'...In the midst of mqtt traffic.  Exiting due to Error: {e}')
            os._exit(1)


    def _read_settings(self) -> dict:
        """INTERNAL METHOD.  Opens the JSON file identified in `settings_filename` and reads in the settings as a dict.
        Raises:
            Exception: When it can't find the file named by the `settings_filename` attribute.  

        Returns:
            dict: including values for the mqtt broker, topic, and vpd setpoints.
        """
        self.logger.debug(f'-> Reading in settings from {settings_filename} file.')
        dict_of_settings = {}
        try:
            with open(settings_filename) as json_file:
                dict_of_settings = json.load(json_file)
        except Exception as e:
            raise Exception(f'Could not open the settings file named {settings_filename}')
        return dict_of_settings

    def _on_connect(self,client, userdata, flags, rc) :
        """INTERNAL METHOD.  Called back by the mqtt library once the code has connected with the broker.  Now we can subscribe to SensorBuddy readings.

        Args:
            client (opaque structure passed along through the mqtt library. It maintains the mqtt client connection to the broker): We got here because the mqtt library found the broker we want to work with and has assigned a session to this client.
            userdata (_type_): Not used.
            flags (_type_): Not used.
            rc (int): return code from the mqtt library connecting with the broker.
        """
        ''''''
        self.logger.debug(f"-> Mqtt connection returned {rc}")
        mqtt_snifferbuddy_topic = self.settings['mqtt_snifferbuddy_topic']
        client.subscribe(mqtt_snifferbuddy_topic)
        self.logger.debug(f'subscribed to topic:{mqtt_snifferbuddy_topic}')


    def _on_message(self, client, userdata, msg) :
        """ INTERNAL METHOD. Received a `tele/snifferbuddy/SENSOR` msg (sensor reading) from SnifferBuddy (obtained through the growbuddy broker).  Next, a new value for the VPD is calculated and the values are sent to the caller if a callback function was provided. 

        Args:
            msg (str):The message is a JSON string sent by SnifferBuddy that looks something like


                {"Time":"2022-09-06T08:52:59",
                "ANALOG":{"A0":542},
                "SCD30":{"CarbonDioxide":814,"eCO2":787,"Temperature":71.8,"Humidity":61.6,"DewPoint":57.9},"TempUnit":"F"}  
             
        """
        message = msg.payload.decode(encoding='UTF-8')
        self.logger.debug(f'mqtt received message...{message}')
        time, air_T, RH, vpd = self._calc_vpd(message)
        if self.values_callback:
            self.values_callback(time,air_T, RH, vpd)

        nSecondsON = self._pid(self.setpoint,vpd)
        self.logger.debug(f'vpd: {vpd}   num seconds to turn humidifier on: {nSecondsON}')
        if nSecondsON > 0:
            self._turn_on_humidifier(nSecondsON)



    
    def _calc_vpd(self, msg_str:str) -> (float):

        """ INTERNAL METHOD. I decided at this point not to measure the leaf temperature but take the much simpler approach of assuming
        2 degrees F less than the air temperature.  Clearly not as accurate as reading.  But for my purposes "good enough."

        Once an mqtt message is received from the GrowBuddy broker that a SnifferBuddy reading is available, _calc_vpd() is called to calculate the VPD.  The mqtt message comes in as a JSON string.  The JSON string is converted to a dictionary.  The dictionary contains the values needed for the VPD calculation.

        The VPD equation comes `from a Quest website <https://www.questclimate.com/vapor-pressure-deficit-indoor-growing-part-3-different-stages-vpd/>`_

        Args:
            msg_str (JSON str): mqtt message in JSON string format.
        Raises:
            Exception: If one of the values needed to calculate the VPD is of a type or value that won't work.

        Returns the calculated VPD value.
        """
        dict = json.loads(msg_str)
        # TODO: Make usable for at least the SCD30 or SCD40
        air_T = dict["SCD30"]["Temperature"]
        RH = dict["SCD30"]["Humidity"]
        time = dict["Time"]
        if not isinstance(air_T,float) or not isinstance(RH,float) or air_T <= 0.0 or RH <= 0.0:
            raise Exception(f'Received unexpected values for either the temperature ({air_T}) or humidity ({RH}) or both')
        leaf_T = air_T -2
        vpd = 3.386*(math.exp(17.863-9621/(leaf_T+460))-((RH/100)*math.exp(17.863-9621/(air_T+460))))
        return(time,air_T,RH,vpd)

    def _pid(self, setpoint:float, reading:float) -> int:
        """INTERNAL METHOD.  This is the code for the `PID controller <https://en.wikipedia.org/wiki/PID_controller>`_

        The PID controller is at the heart of determining how many seconds to turn on the humidifier.  I expect this method to be evolved over time.
        1. I am optimizing for my environment - a climate controlled area with a grow tent.  The temperature is in the 70's F.  The relative humidity is typically around 40-50%.
        2. I am new to PID controllers.  I have to start somewhere, but I am quite sure I will cringe at this code a year from now!

        Args:
            setpoint (float): The ideal value for the VPD.
            reading (float):  The most recent reading.

        Returns:
            int: How many seconds to turn on the humidifier on.
        """
        Kp = self.settings['Kp']
        Ki = self.settings['Ki']
        Kd = self.settings['Kd']
        # This code is designed for my setup.  The indoors is climate cocntrolled.  There is only a humidifier to turn on or off - that is, it is always the case more humidity is needed and
        # the air temperature is a comfortable range for the plants.
        # If setpoint - reading is positive, the air in the grow room is too humid.  Most (pretty much all?) of the time the error should be negative.
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
        self.logger.debug(f'pCorrection is {pCorrection}, iCorrection is {iCorrection}, dCorrection is {dCorrection}')
        # Calculate the # Seconds to turn Humidifier on.  I am roughly guessing 1 second on lowers VPD by .01.  A Wild Guess to be sure.
        nSecondsON = abs( int( (pCorrection + iCorrection + dCorrection)*100 ) )
        self.logger.debug(f'Number of seconds to turn on the Humdifier is {nSecondsON}.')
        return nSecondsON



    def _turn_on_vaporbuddy(self,nSecondsON:int) -> None:
        """Send mqtt messages to the plug_humidifier_fan and plug_humidifier_mister

        Args:
            nSecondsON (int): The number of seconds to turn the mister and fan on.
        """
    #    Sonoff can be sent TOGGLE, ON, OFF in the form of cmnd/vaporbuddy_mister/POWER  how that is done is shown below....
        # Set up a callback to send an OFF message after the humidifier has been on nSecondsON
        timer = threading.Timer(nSecondsON,self._turn_off_humidifier)
        self.client.publish("cmnd/plug_humidifier_fan/POWER","ON")
        self.client.publish("cmnd/plug_humidifier_mister/POWER","ON")
        self.logger.debug(f'-> humidifier turned on for {nSecondsON} seconds.')
        timer.start()

    def _turn_off_vaporbuddy(self):
        """Send mqtt messages to the plug_humidifier_fan and plug_humidifier_mister to turn them off.
        """
        self.client.publish('cmnd/plug_humidifier_fan/POWER',"OFF")
        self.client.publish("cmnd/plug_humidifier_mister/POWER","OFF")
        self.logger.debug('-> _turn_off_humidifer')