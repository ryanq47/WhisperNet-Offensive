# audit logger.

import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
import time
from modules.config import Config
from modules.log import log

application_logger = log(__name__)

class Audit:
    def __init__(self):
        """
        Initializes the action logger.

        NOT printed to screen.   

        :param log_file: Path to the log file.
        :param max_bytes: Maximum file size before rollover (default is 10 MB).
        :param backup_count: Number of backup files to keep (default is 5).
        """
        self.logger = logging.getLogger('ActionLogger')
        self.logger.setLevel(logging.INFO)

        # log_file='action.log', max_bytes=10*1024*1024, backup_count=5
        # Create a rotating file handler
        log_file        = Config().config.server.audit.log.file_name
        max_bytes       = Config().config.server.audit.log.max_file_size
        backup_count    = Config().config.server.audit.log.max_file_backups


        handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def audit(self, data: str|dict):
        """
        Logs an action in FormJ format.
        """

        # Check if data is a dictionary
        if isinstance(data, dict):
            try:
                # Ensure the 'audit' field exists and add a timestamp
                data.setdefault('audit', {})
                data['audit']['timestamp'] = int(time.time())

                # Convert the dictionary to a JSON string and log it
                self.logger.info(json.dumps(data))
            except Exception as e:
                # Fallback if conversion to JSON fails
                print("Could not convert dictionary to JSON string, logging as string instead.")
                self.logger.info(str(data))
        elif isinstance(data, str):
            try:
                # Attempt to log the string directly
                self.logger.info(data)
            except Exception as e:
                # Fallback in case of an unexpected error while logging
                application_logger.warning("Could not log string, printing instead.")
                print(data)
        else:
            # Handle other types (like numbers, lists, etc.) by converting them to a string
            try:
                self.logger.info(str(data))
            except Exception as e:
                application_logger.warning("Could not log data, printing instead.")
                print(data)
