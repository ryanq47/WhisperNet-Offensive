import logging
from logging.handlers import RotatingFileHandler
import json
import time
from modules.config import Config
from modules.log import log

application_logger = log(__name__)

class Audit:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Audit, cls).__new__(cls, *args, **kwargs)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        """
        Initializes the action logger.

        NOT printed to screen.
        """
        self.logger = logging.getLogger('ActionLogger')
        if not self.logger.handlers:  # Prevent adding multiple handlers
            self.logger.setLevel(logging.INFO)

            # Read configuration
            log_file = Config().config.server.audit.log.file_name
            max_bytes = Config().config.server.audit.log.max_file_size
            backup_count = Config().config.server.audit.log.max_file_backups

            handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def audit(self, data: str | dict):
        """
        Logs an action in FormJ format.
        """
        if isinstance(data, dict):
            try:
                data.setdefault('audit', {})
                data['audit']['timestamp'] = int(time.time())
                self.logger.info(json.dumps(data))
            except Exception as e:
                print("Could not convert dictionary to JSON string, logging as string instead.")
                self.logger.info(str(data))
        elif isinstance(data, str):
            try:
                self.logger.info(data)
            except Exception as e:
                application_logger.warning("Could not log string, printing instead.")
                print(data)
        else:
            try:
                self.logger.info(str(data))
            except Exception as e:
                application_logger.warning("Could not log data, printing instead.")
                print(data)
