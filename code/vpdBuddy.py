from vpdController_code import vpdController


def snifferbuddy_values_callback(time: str, air_T: float, RH: float, vpd: float):
    """Returns date/time, air temperature, and relative humidity values vpdController().
    vpdController() recieves mqtt messages from a SnifferBuddy.  It then uses the values
    to calculate the vpd.  Now that we have the values, we can store them into an influxdb
    database for future analysis.

    Args:
        time (str): _description_
        air_T (float): Air Temperature readings that originate from SnifferBuddy.
        RH (float): Relative Humidity readings that originate from SnifferBuddy.
        vpd (float): calculated Vapor Pressure Deficit based on SnifferBuddy readings.
    """
    pass


def main():
    # Create an instance of the vpdController
    myController = vpdController(snifferbuddy_values_callback=snifferbuddy_values_callback)


if __name__ == "__main__":
    main()
