COMPARISON_FUNCTIONS = {
    "StomaBuddy_PID_key": lambda x, max_val: x > max_val,
    "MistBuddy_PID_key": lambda x, max_val: x < max_val,
}


class PID(object):
    def __init__(self, PID_key: str):
        self.maximum = 0.92
        self.comparison_func = COMPARISON_FUNCTIONS.get(
            PID_key, lambda x, max_val: x > max_val
        )

    def __call__(self, current_value) -> float:
        if self.comparison_func(current_value, self.maximum):
            print("No actuator action needed.  Returning.")
            return 0


vpd_pid = PID("MistBuddy_PID_key")
vpd_pid(0.80)
