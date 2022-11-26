import inspect
import logging
import sys
import colors_code


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

         snifferBuddyReadingsInstance = Gus(SnifferBuddyReadings_callback=snifferbuddyreadings, status_callback=status_callback,
                                        SnifferBuddyReadings_table_name="sniff2",log_level=logging.INFO)

    By default, `Gus()` sets the logging level to logging.DEBUG.  By setting the log level to info, any of the logging calls
    set to logging.DEBUG will not occur.  This is how `Python logging normally works <https://docs.python.org/3/howto/logging.html>`_.

   Different colored text will be displayed depending on the logging level.

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
            f"{colors_code.Green}{i.filename}:{i.lineno}  {i.function}   ...{message}{colors_code.Original}"
        )

    def info(self, message):
        f = inspect.currentframe()
        i = inspect.getframeinfo(f.f_back)
        self.logger.info(
            f"{colors_code.Yellow}{i.filename}:{i.lineno}  {i.function}   ...{message}{colors_code.Original}"
        )

    def warning(self, message):
        f = inspect.currentframe()
        i = inspect.getframeinfo(f.f_back)
        self.logger.error(
            f"{colors_code.Red}{i.filename}:{i.lineno}  {i.function}   ...{message}{colors_code.Original}"
        )

    def error(self, message):
        f = inspect.currentframe()
        i = inspect.getframeinfo(f.f_back)
        self.logger.error(
            f"{colors_code.BIRed}{i.filename}:{i.lineno}  {i.function}   ...{message}{colors_code.Original}"
        )

    # def _get_Error_Bad_Soil_Moisture_Reading(self):
    #     return 2000
    # Create a property object
    # Error_Bad_Soil_Moisture_Reading = property(_get_Error_Bad_Soil_Moisture_Reading)
