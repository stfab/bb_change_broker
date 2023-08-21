"""Implementation of a logger that logs to a file."""

import logging
import logging.config


class Logger:
    """A custom logger."""

    def __init__(self, logging_config=None):
        """Initialize the logger.

        :param log_file_name (str): The name of the log file. If None, logs to stdout.
        :param debug_level (int): The debug level of the logger.
        """
        if logging_config is not None:
            logging.config.dictConfig(logging_config)
        else:
            logging.basicConfig(filename="/dev/null", level=logging.CRITICAL)
        self.logger = logging.getLogger("bb_change_broker")

    def debug(self, *args):
        """Log a debug message.

        :param args: The message to log.
        """
        self.logger.debug(*args)

    def info(self, *args):
        """Log an info message.

        :param args: The message to log.
        """
        self.logger.info(*args)

    def warning(self, *args):
        """Log a warning message.

        :param args: The message to log.
        """
        self.logger.warning(*args)

    def error(self, *args):
        """Log an error message.

        :param args: The message to log.
        """
        self.logger.error(*args)

    def stack_trace(self, *args):
        """Log a stack trace.

        :param args: The message to log.
        """
        self.logger.exception(*args)
