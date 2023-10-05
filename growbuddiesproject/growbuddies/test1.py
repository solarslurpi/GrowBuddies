from collections import deque

class YourClass:
    def __init__(self):
        self.device_deques = {}
        self.rolling_window_size = 3  # or whatever size you want

    def add_value(self, name, value):
        if name not in self.device_deques:
            self.device_deques[name] = deque(maxlen=self.rolling_window_size)
        self.device_deques[name].append(value)

    def calculate_average(self):
        # Check if all deques have at least 3 values and the same length
        lengths = [len(deq) for deq in self.device_deques.values()]
        if len(set(lengths)) == 1 and lengths[0] >= self.running_window_size:
            # Calculate the average across all deques
            all_values = [val for deq in self.device_deques.values() for val in deq]
            return sum(all_values) / len(all_values)
        else:
            return "Cannot calculate average, deques have different lengths or less than 3 values"

# Create an instance and add some test values
your_instance = YourClass()
your_instance.add_value('daisy', 1)
your_instance.add_value('sunshine', 2)
print(your_instance.calculate_average())
your_instance.add_value('daisy', 3)
your_instance.add_value('sunshine', 4)
your_instance.add_value('daisy', 5)
your_instance.add_value('sunshine', 6)

# Attempt to calculate the average
print(your_instance.calculate_average())  # Should output the average since both deques have at least 3 values and the same length
