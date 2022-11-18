import logging
# TODO: These two lines can be removed when this is part of a package.
import sys
sys.path.append('/home/pi/growbuddy/code')
from growbuddy_code import growBuddy


current_soil_moisture_reading = 0


class SoilMoistureBuddy(growBuddy):
    def __init__(self):
        super().__init__(growBuddy_values_callback=self.values_callback, log_level=logging.DEBUG)

    def values_callback(self, dict):
        global current_soil_moisture_reading
        current_soil_moisture_reading = soil_moisture_reading = dict['ANALOG']['A0']
        self.logger.info(f'Moisture sensor value is {soil_moisture_reading}')


class CalibrateCapacitiveTouchSensor(growBuddy):
    def __init__(self):
        super().__init__(growBuddy_values_callback=self.values_callback, log_level=logging.DEBUG)

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
    # Start Getting Soil Moisture Readings
    SoilMoistureBuddy()
    # Add Listening for Calibration messages.
    CalibrateCapacitiveTouchSensor()
    while True:
        pass
