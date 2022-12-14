import logging
from growbuddies.logginghandler import LoggingHandler
from growbuddies.gus import Gus

logger = LoggingHandler(logging.DEBUG)

current_reading = None


class GetCapacitiveTouchSensorReadings(Gus):
    def __init__(self):
        super().__init__(readings_callback=self.dripBuddy_callback, status_callback=self.status_callback, topic_key="dripBuddy_topic")

    def status_callback(self, status):
        """`Gus()` will call this function when an `LWT` packet comes in.  `Gus()` returns a string with either
        `online` or `offline`.

        Args:
            status (str): `Gus()` sends either the string "Online" or "Offline".
        """
        logger.debug(f'-> dripBuddy is: {status}')

    def dripBuddy_callback(self, readings_dict):
        global current_reading
        current_reading = readings_dict["ANALOG"]["A0"]
        logger.debug(f'the current reading is {current_reading}')


class CalibrateReadings(Gus):
    def __init__(self):
        super().__init__(readings_callback=self.calibrate_callback, status_callback=self.status_callback, topic_key="dripBuddy_calibrate_topic")

    def status_callback(self, status):
        """`Gus()` will call this function when an `LWT` packet comes in.  `Gus()` returns a string with either
        `online` or `offline`.

        Args:
            status (str): `Gus()` sends either the string "Online" or "Offline".
        """
        logger.debug(f'-> dripBuddy is: {status}')

    def calibrate_callback(self, tensiometer_reading):
        global current_reading
        logger.debug(f"calibration returned reading of {tensiometer_reading}")
        # measurement = "dripbuddy_calibration"
        # influx_data = [{"measurement": measurement,
        #                 "fields": {"tensiometer": tensiometer_reading,
        #                            "capacitive": current_reading
        #                            }
        #                 }
        #                ]
        fields = {"tensiometer": tensiometer_reading,
                  "capacitive": current_reading
                  }
        self.db_write("dripbuddy_calibration", fields)
        self.logger.info(f'Calibration data point.  DripBuddy value is {current_reading}. '
                         'Tensiometer value is {tensiometer_reading}.')


def main():

    sensor_readings = GetCapacitiveTouchSensorReadings()
    sensor_readings.start()
    calibration_readings = CalibrateReadings()
    calibration_readings.start()

    while True:
        pass


if __name__ == '__main__':
    main()
