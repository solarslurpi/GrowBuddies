import threading
import time

# Task to be executed at regular intervals.
def timer():
    while True:
        print("Hello world!")
        time.sleep(3)   # 3 seconds.

# Start execution in the background.
t = threading.Thread(target=timer)
t.start()