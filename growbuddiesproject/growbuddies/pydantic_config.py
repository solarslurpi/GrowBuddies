# Maps to the field in growbuddies_settings.json *_PID_config.
from pydantic import BaseModel, Field
from typing import List


class PIDConfig(BaseModel):
    name: str
    setpoint: float
    Kp: float
    Ki: float
    Kd: float
    output_limits: List[int] = Field(..., min_items=2, max_items=2)
    integral_limits: List[int] = Field(..., min_items=2, max_items=2)
    tune_increment: float
    comparison_function: str
    mqtt_power_topics: List[str]
    incoming_port: int = Field(..., gt=0, lt=65536)
    mean_values_input_port: int = Field(..., gt=0, lt=65536)
    store_readings_output_port: int = Field(..., gt=0, lt=65536)
    telegraf_fieldname: str
    num_bias_seconds_on: int
