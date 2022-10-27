
def get_SnifferBuddy_dict(dict):
    # What type of sensor?  Currently handling just the SCD30.
    # TODO: Other air quality sensors.
    snifferbuddy_dict = {}
    a = snifferbuddy_dict["air_T"] = dict["SCD30"]["Temperature"]
    r = snifferbuddy_dict["RH"] = dict["SCD30"]["Humidity"]
    l = snifferbuddy_dict["light_level"] = dict["ANALOG"]["A0"]
    if (
        not isinstance(a, float)
        or not isinstance(r, float)
        or not isinstance(l, int)
        or a <= 0.0
        or r <= 0.0
        or l < 0
        or l > 1024
    ):
        raise Exception(
            f"Values received:\n  Air Temperature: {a},\n Relative Humidity: {r},Light_level: {l}.\n\n  One or all of these values are out of range of what was expected.")
    return snifferbuddy_dict