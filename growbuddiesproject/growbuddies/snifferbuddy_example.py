#############################################################################
# SPDX-FileCopyrightText: 2023 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################

from growbuddies.snifferbuddy_handler import SnifferBuddyHandler
import time


def main():
    """
    **snifferbuddy_example.py**

    This script initializes a SnifferBuddyHandler :ref:`SnifferBuddyHandler  <_snifferbuddyhandler>`.  The handler knows how to handle SnifferBuddy MQTT messages and is able to return SnifferBuddy values and status messages by placing them into a Python queue.  The script continuously checks the handler's queue for new SnifferBuddy readings or status messages until interrupted with a KeyboardInterrupt (Ctrl+C).  If a message is found, it will be printed out.
    """
    handler = SnifferBuddyHandler()
    handler.start()
    try:
        while True:
            message = handler.get_message_from_queue()
            if message is not None:
                message_type, message_content = message
                print(f"Received {message_type} message: {message_content}")

            time.sleep(5)
    except KeyboardInterrupt:
        handler.stop()


if __name__ == "__main__":
    main()
