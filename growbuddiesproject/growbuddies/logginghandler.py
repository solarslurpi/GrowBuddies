#
# Adds the ability to log progress, warnings, errors.  The color of the text is dependent on the log level.
#
# Copyright 2022 Happy Day

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
import inspect
import logging
import sys
import growbuddies.colors as colors
from growbuddies.settings_code import Settings


class LoggingHandler:
    """Sprinkling code liberally with logging lines helps debugging and also helps to figure out what is going wrong.

     .. note::

         The parameter to LoggingHandler looks to be 10.  This is because the parser resolved logging.DEBUG.

     .. tip::
         If you are new to Python logging, it helps to get an overview - particularly about log levels from
         `The Python logging documentation <https://docs.python.org/3/howto/logging.html>`_.

     For example, let's make an instance of a `SnifferBuddyReadings()` with logging sent to informational:

     .. code-block:: python
          :caption: Initializing `Gus()` with the log level set to INFO.

          snifferBuddyReadingsInstance = Gus(readings_callback=snifferbuddyreadings, status_callback=status_callback,
                                         table_name="sniff2",log_level=logging.INFO)

     By default, `Gus()` sets the logging level to logging.DEBUG.  By setting the log level to info, any of the logging calls
     set to logging.DEBUG will not occur.  This is how `Python logging normally works <https://docs.python.org/3/howto/logging.html>`_.

    Different colored text will be displayed depending on the logging level.

    """

    def __init__(self):
        settings = Settings()
        settings.load()
        # Extract the logging level
        log_level_str = settings.get("log_level")
        try:
            log_level = logging.getLevelName(log_level_str)
        except Exception as e:
            raise Exception(f"Could not set up the logging level with {log_level} as the level name.  Error: {e}")

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
        self.logger.debug(f"{colors.Green}{i.filename}:{i.lineno}  {i.function}   ...{message}{colors.Original}")

    def info(self, message):
        f = inspect.currentframe()
        i = inspect.getframeinfo(f.f_back)
        self.logger.info(f"{colors.Yellow}{i.filename}:{i.lineno}  {i.function}   ...{message}{colors.Original}")

    def warning(self, message):
        f = inspect.currentframe()
        i = inspect.getframeinfo(f.f_back)
        self.logger.error(f"{colors.Red}{i.filename}:{i.lineno}  {i.function}   ...{message}{colors.Original}")

    def error(self, message):
        f = inspect.currentframe()
        i = inspect.getframeinfo(f.f_back)
        self.logger.error(f"{colors.BIRed}{i.filename}:{i.lineno}  {i.function}   ...{message}{colors.Original}")

    # def _get_Error_Bad_Soil_Moisture_Reading(self):
    #     return 2000
    # Create a property object
    # Error_Bad_Soil_Moisture_Reading = property(_get_Error_Bad_Soil_Moisture_Reading)
