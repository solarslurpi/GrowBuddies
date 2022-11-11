import logging
from growBuddy_code import growBuddy

current_soil_moisture_reading = 0


class SoilMoistureBuddy(growBuddy):
    def __init__(self):
        super().__init__("readSoilMoisture",
                         values_callback=self.values_callback,
                         log_level=logging.INFO)

    def values_callback(self, dict):
        global current_soil_moisture_reading
        current_soil_moisture_reading = soil_moisture_reading = dict['ANALOG']['A0']
        self.logger.info(f'Moisture sensor value is {soil_moisture_reading}')
        if soil_moisture_reading == self.logger.Error_Bad_Soil_Moisture_Reading:
            self.logger.error(f'ERROR! bad moisture sensor reading!')
        # Name of measurement table in InfluxDB.  Data is the json formatted reading that will be stored in influxDB.
        measurement = "soil_moisture_readings"
        influx_data = [
        {
            "measurement": measurement,

                "fields": {
                    "moisture" : soil_moisture_reading,
                }
            }
        ]
        self.db_write(influx_data)

class CalibrateCapacitiveTouchSensor(growBuddy):
    def __init__(self):
        super().__init__("calibrateSoilMoisture",values_callback=self.values_callback,log_level=logging.INFO)

    def values_callback(self,tensiometer_reading):
        global current_soil_moisture_reading
        if current_soil_moisture_reading <= 0:
            # skip
            self.logger.info(f'Not saving calibration data. The current moisture reading is {current_soil_moisture_reading}.')
            return

        measurement = "soil_moisture_calibration"
        influx_data = [
        {
            "measurement": measurement,

                "fields": {
                    "tensiometer" : tensiometer_reading,
                    "capacitive" : current_soil_moisture_reading
                }
            }
        ]
        self.db_write(influx_data)

        self.logger.info(f'Calibration data point.  Moisture Sensor value is {current_soil_moisture_reading}. Tensiometer value is {tensiometer_reading}.')

if __name__ == '__main__':
    # Start Getting Soil Moisture Readings
    SoilMoistureBuddy()
    # Add Listening for Calibration messages.
    CalibrateCapacitiveTouchSensor()
    while True:
        pass
