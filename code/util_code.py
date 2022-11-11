import math


def calc_vpd(temperature: float, humidity: float) -> (float):

    """INTERNAL METHOD. I decided at this point not to measure the leaf temperature but take the much simpler
    approach of assuming 2 degrees F less than the air temperature.  Clearly not as accurate as reading.  But for
    my purposes "good enough."

    Once an mqtt message is received from the growBuddy broker that a SnifferBuddy reading is available, _calc_vpd()
    is called to calculate the VPD.  The mqtt message comes in as a JSON string.  The JSON string is converted to a
    dictionary.  The dictionary contains the values needed for the VPD calculation.

    The VPD equation comes
    `from a Quest website <https://www.questclimate.com/vapor-pressure-deficit-indoor-growing-part-3-different-stages-vpd/>`_

    Args:
        dict (dict): Dictionary of values returned from an mqtt message.
    Raises:
        Exception: If one of the values needed to calculate the VPD is of a type or value that won't work.

    Returns the calculated VPD value.
    """
    # TODO: Make usable for at least the SCD30 or SCD40
    air_T = temperature
    RH = humidity
    if (
        not isinstance(air_T, float) or not isinstance(RH, float) or air_T <= 0.0 or RH <= 0.0
    ):
        raise Exception(
            f"Received unexpected values for either the temperature ({air_T}) or humidity ({RH}) or both"
        )
    leaf_T = air_T - 2
    vpd = 3.386 * (
        math.exp(17.863 - 9621 / (leaf_T + 460)) - ((RH / 100) * math.exp(17.863 - 9621 / (air_T + 460)))
    )
    return round(vpd, 2)
