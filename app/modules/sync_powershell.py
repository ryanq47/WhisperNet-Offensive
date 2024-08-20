"""
Form_J Sync Key Handler for powershell 

"""

import munch
from modules.log import log

logger = log(__name__)


class FormJPowershell:
    def __init__(self, data: munch.Munch):
        self.data = data

        for entry in self.data:
            self.process(entry)

    def process(self, entry):
        """process data"""

        logger.debug(entry)
