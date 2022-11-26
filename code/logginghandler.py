import inspect
import logging
import sys
#
# See https://gist.github.com/vratiu/9780109
#

# Regular Colors
Black = "\[\033[0;30m\]"  # Black
Red = "\[\033[0;31m\]"  # Red
Green = "\[\033[0;32m\]"  # Green
Yellow = "\[\033[0;33m\]"  # Yellow
Blue = "\[\033[0;34m\]"  # Blue
Purple = "\[\033[0;35m\]"  # Purple
Cyan = "\[\033[0;36m\]"  # Cyan
White = "\[\033[0;37m\]"  # White
Original = "\033[m"  # reset to original (off-white)

# Bold
BBlack = "\[\033[1;30m\]"  # Black
BRed = "\[\033[1;31m\]"  # Red
BGreen = "\[\033[1;32m\]"  # Green
BYellow = "\[\033[1;33m\]"  # Yellow
BBlue = "\[\033[1;34m\]"  # Blue
BPurple = "\[\033[1;35m\]"  # Purple
BCyan = "\[\033[1;36m\]"  # Cyan
BWhite = "\[\033[1;37m\]"  # White
# Bold High Intensty
BIBlack = "\[\033[1;90m\]"  # Black
BIRed = "\[\033[1;91m\]"  # Red
BIGreen = "\[\033[1;92m\]"  # Green
BIYellow = "\[\033[1;93m\]"  # Yellow
BIBlue = "\[\033[1;94m\]"  # Blue
BIPurple = "\[\033[1;95m\]"  # Purple
BICyan = "\[\033[1;96m\]"  # Cyan
BIWhite = "\[\033[1;97m\]"  # White


class LoggingHandler:
    """The LoggingHandler class simplifies logging so that we can have insight
    into what is going on when our Python Script is run.  While debugging, the code
    is typically liberally sprinkled with debug log entries.

    .. tip::
        If you are new to Python logging, it helps to get an overview - particularly about log levels from
        :ref:`The Python logging documentation <https://docs.python.org/3/howto/logging.html>`.

    For example, let's make an instance of a `SnifferBuddyReadings()` with logging sent to informational:

    .. code-block:: python
         :caption: Initializing `Gus()` with the log level set to INFO.

         snifferBuddyReadingsInstance = Gus(SnifferBuddyReadings_callback=snifferbuddyreadings, status_callback=status_callback,
                                        SnifferBuddyReadings_table_name="sniff2",log_level=logging.INFO)


    By default, `Gus()` sets the logging level to logging.DEFAULT.  By setting the log level to info, any of the logging calls
    set to logging.DEBUG will not occur.  This is how [Python logging normally works](https://docs.python.org/3/howto/logging.html).

    ```
    Oct 05 14:32:14 growBuddy python3.7[1286]: 2022-10-05 14:32:14,464:DEBUG:\[\]/home/pi/growBuddy/code/growBuddy.py:44  __init__
    ...-> Initializing growBuddy class for task readSoilMoisture
    ```

    Setting the logging level to logging.DEBUG makes sense as we write or debug the code.  Once those
    tasks have been completed, setting the logging level to logging.INFO and then running the Script will
    not include statements when the logging is set at logging.DEBUG.

    """

    def __init__(self, log_level=logging.DEBUG):

        # Multiple calls to getLogger() with the same name will always return a reference to the same Logger object.
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.hasHandlers():
            formatter = logging.Formatter("%(asctime)s:%(message)s")
            handler = logging.StreamHandler(stream=sys.stdout)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def debug(self, message):
        f = inspect.currentframe()
        i = inspect.getframeinfo(f.f_back)
        self.logger.debug(
            f"{Green}{i.filename}:{i.lineno}  {i.function}   ...{message}{Original}"
        )

    def info(self, message):
        f = inspect.currentframe()
        i = inspect.getframeinfo(f.f_back)
        self.logger.info(
            f"{Yellow}{i.filename}:{i.lineno}  {i.function}   ...{message}{Original}"
        )

    def warning(self, message):
        f = inspect.currentframe()
        i = inspect.getframeinfo(f.f_back)
        self.logger.error(
            f"{BIRed}{i.filename}:{i.lineno}  {i.function}   ...{message}{Original}"
        )

    def error(self, message):
        f = inspect.currentframe()
        i = inspect.getframeinfo(f.f_back)
        self.logger.error(
            f"{BIRed}{i.filename}:{i.lineno}  {i.function}   ...{message}{Original}"
        )

    # def _get_Error_Bad_Soil_Moisture_Reading(self):
    #     return 2000
    # Create a property object
    # Error_Bad_Soil_Moisture_Reading = property(_get_Error_Bad_Soil_Moisture_Reading)
