# import logging


class snifferBuddy:

    def _get_temperature(self):
        if self.sensor == "SCD30":
            return float(self.mqtt_dict["SCD30"]["Temperature"])
        else:
            raise Exception(f" The {self.sensor} is an unknown snifferBuddy type.")

    def _set_temperature(self):
        pass

    def __init__(self, mqtt_dict, sensor="SCD30"):
        self.sensor = sensor
        self.mqtt_dict = mqtt_dict
        self.temperature = property(self._get_temperature, self._set_temperature)


