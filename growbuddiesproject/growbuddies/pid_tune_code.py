import threading
import time


class PID_Tune:
    def __init__(self, initial_kp, tune_increment, stability_time, update_Kp_callback):
        """
        Initialize the PID_Tune class.

        Args:
        initial_kp (float): Initial Kp value for the tuning process.
        tune_increment (float): Increment value for adjusting Kp during tuning.
        stability_time (int): Time in seconds to wait for the system to stabilize after each Kp update.
        update_callback (function): Callback function to update the Kp value in the main PID controller.
        """
        self.Kp = initial_kp
        self.tune_increment = tune_increment
        self.stability_time = stability_time
        self.update_Kp_callback = update_Kp_callback
        self.tuning_thread = None
        self.is_tuning = False

    def start_tuning(self):
        """Start the tuning process in a separate thread."""
        if not self.is_tuning:
            self.is_tuning = True
            self.tuning_thread = threading.Thread(target=self._tuning_loop)
            self.tuning_thread.start()

    def stop_tuning(self):
        """Stop the tuning process."""
        if self.is_tuning:
            self.is_tuning = False
            self.tuning_thread.join()

    def _tuning_loop(self):
        """Tuning loop that runs in a separate thread."""
        while self.is_tuning:
            self.Kp += self.tune_increment
            self.update_Kp_callback(self.Kp)
            time.sleep(self.stability_time)

    def __repr__(self):
        tuning_state = "Running" if self.is_tuning else "Stopped"
        thread_info = (
            f", ThreadID={self.tuning_thread.ident}" if self.tuning_thread else ""
        )
        return (
            f"<PID_Tune Kp={self.Kp}, "
            f"Increment={self.tune_increment}, "
            f"StabilityTime={self.stability_time}s, "
            f"State={tuning_state}"
            f"{thread_info}>"
        )
