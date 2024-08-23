# audit logger.

import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
import time

class Audit:
    def __init__(self, log_file='action.log', max_bytes=10*1024*1024, backup_count=5):
        """
        Initializes the action logger.

        NOT printed to screen.   

        :param log_file: Path to the log file.
        :param max_bytes: Maximum file size before rollover (default is 10 MB).
        :param backup_count: Number of backup files to keep (default is 5).
        """
        self.logger = logging.getLogger('ActionLogger')
        self.logger.setLevel(logging.INFO)

        # Create a rotating file handler
        handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_action(self, data):
        """
        Logs an action in FormJ format.
        """

        # Log the action as a JSON string
        try:
            # add timestamp 
            data.setdefault('audit', {})
            # Add Unix timestamp to the audit field
            data['audit']['timestamp'] = int(time.time()) 

            self.logger.info(json.dumps(data))
        except Exception as e:
            # just in case shit gets fucked up
            print("Could not convert entry to json string, printing as string")
            self.logger.info(str(data))

