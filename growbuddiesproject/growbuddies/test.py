import json

# Mock API function for CO2 calibration
def forcedCalibration(calibration_value):
    print(f"CO2 calibration value set to {calibration_value}")

# Process calibration message and update devices dictionary
def process_calibration_message(topic, payload, devices, current_readings):
    _, _, device, param_type = topic.split('/')
    calibration_value = int(payload)

    if param_type == "co2":
        forcedCalibration(calibration_value)
        return

    if device not in devices:
        devices[device] = {"temperature": 0, "humidity": 0}

    current_value = current_readings[device].get(param_type, 0)
    offset_value = calibration_value - current_value
    devices[device][param_type] = offset_value

# Update settings JSON with new devices dictionary
def update_settings_json(devices, json_path):
    try:
        with open(json_path, 'r') as f:
            existing_settings = json.load(f)
    except FileNotFoundError:
        existing_settings = {}

    if 'devices' in existing_settings:
        for device, params in devices.items():
            if device in existing_settings['devices']:
                existing_settings['devices'][device].update(params)
            else:
                existing_settings['devices'][device] = params
    else:
        existing_settings['devices'] = devices

    with open(json_path, 'w') as f:
        json.dump(existing_settings, f, indent=4)

# Initialize devices dictionary
devices = {}

# Mock current readings for devices
current_readings = {
    'daisy': {'temperature': 66, 'humidity': 38},
    'rosie': {'temperature': 68, 'humidity': 43}
}

# Simulated calibration messages
calibration_messages = [
    ("snifferbuddy/calibrate/daisy/temperature", "68"),
    ("snifferbuddy/calibrate/daisy/humidity", "40"),
    ("snifferbuddy/calibrate/rosie/temperature", "70"),
    ("snifferbuddy/calibrate/rosie/humidity", "45"),
    ("snifferbuddy/calibrate/rosie/co2", "400")
]

# Process messages and update devices
for topic, payload in calibration_messages:
    process_calibration_message(topic, payload, devices, current_readings)

# Show final readings
print(f"Final Readings: {devices}")

# Path to the settings JSON
json_path = "/path/to/settings.json"

# Update the settings JSON
update_settings_json(devices, json_path)
