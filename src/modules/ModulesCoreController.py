import logging
from logging.handlers import TimedRotatingFileHandler
import os


class ModulesCoreController:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging()

    def setup_logging(self):
        # Set the logging level
        self.logger.setLevel(logging.DEBUG)

        # Ensure log directory exists
        if not os.path.exists('log'):
            os.makedirs('log')

        # Create a timed rotating file handler
        # The 'midnight' argument means the log will rotate at midnight
        log_filename = os.path.join('log', 'application.log')
        fh = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=7)  # backupCount keeps the last 7 logs
        fh.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s.%(funcName)s - %(levelname)s - %(message)s')

        # Add formatter to the handler
        fh.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(fh)
