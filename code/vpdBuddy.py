from vpdController_code import vpdController


def snifferbuddy_values_callback(sniffer_dict):
    """Returns date/time, air temperature, and relative humidity values vpdController().
    vpdController() recieves mqtt messages from a SnifferBuddy.  It then uses the values
    to calculate the vpd.  Now that we have the values, we can store them into an influxdb
    database for future analysis.

    Args:
        time (str): The date and time the reading was taken (based on the Rasp Pi's date/time).
        air_T (float): Air Temperature readings that originate from SnifferBuddy.
        RH (float): Relative Humidity readings that originate from SnifferBuddy.
        vpd (float): Calculated Vapor Pressure Deficit based on SnifferBuddy readings.
    """
    print(f"sniffer_dict: {sniffer_dict}")


def main():
    # Create an instance of the vpdController
    myController = vpdController(snifferbuddy_values_callback=snifferbuddy_values_callback)
    myController.start()


if __name__ == "__main__":
    main()
