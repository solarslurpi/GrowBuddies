def convert_to_celsius(temp):
    """
    Converts a temperature from Fahrenheit to Celsius if temp > 40.

    Parameters:
    - temp (float): The temperature value.

    Returns:
    - float: The temperature value in Celsius.
    """
    return (temp - 32) * 5.0/9.0 if temp > 40 else temp

def calculate_bounds(value, measurement_type, ambient_temperature=None):
    """
    Calculate the lower and upper bounds for CO2, temperature, and humidity measurements.

    Parameters:
    - value (float): The measured value.
    - measurement_type (str): The type of measurement ('CO2', 'temperature', 'humidity').
    - ambient_temperature (float, optional): The ambient temperature, required for humidity accuracy calculations.

    Returns:
    - tuple: The lower and upper bounds of the measurement.
    """
    # Convert Fahrenheit to Celsius if necessary
    if measurement_type == 'temperature':
        value = convert_to_celsius(value)
    if measurement_type == 'humidity':
        ambient_temperature = convert_to_celsius(ambient_temperature)


    if measurement_type == 'CO2':
        # Reference: Datasheet Section 1.1, SCD40 CO2 measurement accuracy
        if 400 <= value <= 2000:
            accuracy = 50 + 0.05 * value
        elif 2001 <= value <= 5000:
            accuracy = 40 + 0.05 * value
        else:
            raise ValueError('Value out of specified range')
    elif measurement_type == 'temperature':
        # Reference: Datasheet Section 1.3, Temperature Sensing Performance
        if 15 <= value <= 35:
            accuracy = 0.8
        # I think it is weird to have the overlap in this logic, but it is in the spec...
        elif -10 <= value <= 60:
            accuracy = 1.5
        else:
            raise ValueError('Value out of specified range')
    elif measurement_type == 'humidity':
        # Reference: Datasheet Section 1.2, Humidity Sensing Performance
        if 15 <= ambient_temperature <= 35 and 20 <= value <= 65:
            accuracy = 6  # accuracy in %RH
        elif -10 <= ambient_temperature <= 60 and 0 <= value <= 100:
            accuracy = 9  # accuracy in %RH
        else:
            raise ValueError('Value or temperature out of specified range')
    else:
        raise ValueError('Invalid measurement type')

    lower_bound = value - accuracy
    upper_bound = value + accuracy
    if measurement_type == "temperature":
        lower_bound = lower_bound * 9/5 + 32
        upper_bound = upper_bound * 9/5 + 32

    return round(lower_bound, 1), round(upper_bound, 1)

# Examples
co2_value = 600  # example CO2 value in ppm
temperature_value = 71  # example temperature value in Fahrenheit (used for temperature accuracy calc)
humidity_value = 60  # example humidity value in %RH
ambient_temperature = 71  # ambient temperature in Fahrenheit (used for Humidity accuracy calc)

co2_bounds = calculate_bounds(co2_value, 'CO2', ambient_temperature)
temperature_bounds = calculate_bounds(temperature_value, 'temperature', ambient_temperature)
humidity_bounds = calculate_bounds(humidity_value, 'humidity', ambient_temperature)

print(f'CO2 Bounds: ({co2_bounds[0]:.1f}, {co2_bounds[1]:.1f})')
print(f'Temperature Bounds: ({temperature_bounds[0]:.1f}, {temperature_bounds[1]:.1f})')
print(f'Humidity Bounds: ({humidity_bounds[0]:.1f}, {humidity_bounds[1]:.1f})')

