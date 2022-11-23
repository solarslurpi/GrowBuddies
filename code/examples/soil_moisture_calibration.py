import logging

# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growbuddy/code')
from logging_handler import LoggingHandler
from code.gus_code import growBuddy
from snifferbuddy_code import snifferBuddy


current_soil_moisture_reading = 0


class GrabSnifferReadings(growBuddy):
    def __init__(self):
        super().__init__(growBuddy_values_callback=self.values_callback, log_level=logging.DEBUG)

    def values_callback(self, snifferBuddy_dict: snifferBuddy):
        global current_soil_moisture_reading
        current_soil_moisture_reading = soil_moisture_reading = snifferBuddy_dict.light_level
        self.logger.info(f'Moisture sensor value is {soil_moisture_reading}')


class CalibrateCapacitiveTouchSensor(growBuddy):
    def __init__(self, calibration_topic: str):
        super().__init__(growBuddy_values_callback=self.values_callback, topic_key=calibration_topic, log_level=logging.DEBUG)

    def values_callback(self, tensiometer_reading):
        global current_soil_moisture_reading
        if current_soil_moisture_reading <= 0:
            # skip
            self.logger.info(f'Not saving calibration data. The current moisture reading is {current_soil_moisture_reading}.')
            return

        measurement = "soil_moisture_calibration"
        influx_data = [{"measurement": measurement,
                        "fields": {"tensiometer": tensiometer_reading,
                                   "capacitive": current_soil_moisture_reading
                                   }
                        }
                       ]
        self.db_write(influx_data)

        self.logger.info(f'Calibration data point.  Moisture Sensor value is {current_soil_moisture_reading}. '
                         'Tensiometer value is {tensiometer_reading}.')


if __name__ == '__main__':
    # Snag the snifferBuddy readings.
    getSnifferBuddyReadings = GrabSnifferReadings()
    getSnifferBuddyReadings.start()
    # Grab the settings file so the soil_moisture_calibration_topic can be looked up.
    settings_file = getSnifferBuddyReadings.read_settings()
    # Add Listening for Calibration messages.
    try:
        calibration_topic = settings_file["mqtt"]["soil_moisture_calibration_topic"]
    except Exception as e:
        logger = LoggingHandler(logging.DEBUG)
        logger.error(f"Error! trying to read calibration_topic from the settings_file.  Error: {e}")
    calibrateToSensor = CalibrateCapacitiveTouchSensor(calibration_topic)
    calibrateToSensor.start
    while True:
        pass
