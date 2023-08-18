"""Implementation of a logger that logs to a file."""

import logging


class Logger:
    """A custom logger."""

    def __init__(self, log_file_name=None, debug_level=logging.DEBUG):
        """Initialize the logger.

        :param log_file_name (str): The name of the log file. If None, logs to stdout.
        :param debug_level (int): The debug level of the logger.
        """
        self.log_file_name = log_file_name
        self.logger = logging.getLogger("bb_change_broker")
        self.logger.setLevel(logging.DEBUG)
        format = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        handler = (
            logging.FileHandler(log_file_name)
            if log_file_name is not None and log_file_name != ""
            else logging.StreamHandler()
        )
        handler.setFormatter(format)
        handler.setLevel(debug_level)
        # Disable pika logging
        logging.getLogger("pika").setLevel(logging.CRITICAL)

        # TODO: This is a hack to prevent duplicate log messages 
        # Investigate why the class is instantiated multiple times
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(handler)
        elif (
            len(self.logger.handlers) == 1
            and self.logger.handlers[0].__class__ != logging.FileHandler
            and handler.__class__ == logging.FileHandler
        ):
            self.logger.handlers = []
            self.logger.addHandler(handler)

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
