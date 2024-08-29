'''
Form J implementation. 
'''

import munch
import json
from app.modules.log import log
import uuid
import time
#from sync_powershell import FormJPowershell

logger = log(__name__)


# list of sync_key handlers
#handlers = {"Powershell": FormJPowershell}  # self.handle_client_name,


class FormJ:
    def __init__(self, data: dict | str):
        # validate data is a dict based on input.
        # Check if the data is a JSON string
        if isinstance(data, str):
            try:
                logger.debug(
                    f"Type of input: {type(data)}, attempting to parse JSON string."
                )
                self.data = json.loads(data)
                logger.debug("Json string parsed successfully")
            except json.JSONDecodeError as e:
                # If the string is not valid JSON, log an error and raise the exception
                logger.error(f"Failed to decode JSON string: {e}")
                raise e
        elif isinstance(data, dict):
            # If data is already a dictionary, assign it directly
            self.data = data
        else:
            # Handle the case where data is neither a string nor a dictionary
            logger.error(f"Unsupported data type: {type(data)}. Expected str or dict.")
            raise TypeError(
                f"Unsupported data type: {type(data)}. Expected str or dict."
            )


        # validate actual contents
        required_keys = ["rid", "data", "message", "status", "timestamp"]
        for key in required_keys:
            if key not in self.data:
                logger.error(f"Missing required field: {key}")
                raise KeyError(f"Missing required field: {key}")

        # Addtl validation for input data types
        if not isinstance(self.data.get("rid"), str):
            logger.error("Invalid type for 'rid'")
            raise TypeError("The 'rid' field must be a string.")

        if not isinstance(self.data.get("status"), int):
            logger.error("Invalid type for 'status'")
            raise TypeError("The 'status' field must be an int.")

        if not isinstance(self.data.get("timestamp"), int):
            logger.error("Invalid type for 'timestamp'")
            raise TypeError("The 'timestamp' field must be an int.")

        if not isinstance(self.data.get("data"), dict):
            logger.error("Invalid type for 'data'")
            raise TypeError("The 'data' field must be an dict.")

        self.handlers = {
            #'listenerHTTP': ListenerHttpSync #self.handle_client_name,
        }

    def parse(self) -> munch.munchify:
        """
        Munch the input data, and return the munchified data back. Also sets self.data to the transformed munch data

        """
        try:
            # make sure data is not already munch.Munch
            if not isinstance(self.data, munch.Munch):
                # parse stuff into munch, turn self.data into munched
                munched_data = munch.munchify(self.data)
                self.data = munched_data
                return munched_data
            else:
                logger.debug("self.data is already munch data")
                return self.data

        except Exception as e:
            logger.debug(e)
            raise e

    def process(self):
        try:
            # Ensure that `self.data` is of Munch type; if not, convert it from dict to munch
            if not isinstance(self.data, munch.Munch):
                # turn data info munch object
                self.parse()

            # Loop over the 'data' section in the munched object and process each subkey
            # print("Parse values of self.data.data:")
            # for key, value in self.data.data.items():
            # print(f"[+] {key}: {value}")
            # send subkey to handler

            # send to data
            self._process_data()

        except Exception as e:
            logger.debug(e)
            raise e

    def _process_data(self):
        """Handles data feild, operates on self.data"""
        data = self.data.data

        try:
            # Iterate over the sync keys in the data field
            for sync_key, sync_data in data.items():
                _class = handlers.get(sync_key)

                if _class is None:
                    logger.info(f"Sync Key {sync_key} not supported")
                else:
                    # Pass the entire dict (sync_data) in sync_key to the handler
                    _class(data=sync_data)

        except Exception as e:
            logger.error(e)
            raise e

    @staticmethod
    def generate(
        message: str = "",
        data: dict = None,
        data_items: list = None,
        status: int = 200,
    ) -> tuple:
        """
        Helper function to create/construct a formj

        Args:
            status (str): Status of the response, e.g., "success" or "failure".
            data (dict): Data to be sent back in the response.
            error_message (str): Error message, if any.
            data_items (list): List of tuples (key, value) to add to the data dict.
            status_code (int): status code to send back

        Returns:
            tuple: A tuple containing the JSON response and the status code.
        """
        try:
            # Initialize response structure
            response = {
                "rid": generate_unique_id(),  # Unique identifier for this response
                "timestamp": generate_timestamp(),  # Current timestamp
                "status": status,  # not needed, but nice to have
                "data": data if data else {},
                "message": str(message),
            }

            # Add additional data items if provided
            if data_items:
                for key, value in data_items:
                    response["data"][key] = value

            # Remove data key if it has no useful content
            if not response["data"]:
                del response["data"]

            # Return JSON response with appropriate status code
            return response #jsonify(response), status

        except Exception as e:
            logger.error(e)
            raise e

def generate_unique_id() -> str:
    """
    Generate a unique message ID using UUIDv4.

    Returns:
        str: A unique UUIDv4 string.
    """
    return str(uuid.uuid4())


@staticmethod
def generate_timestamp() -> int:
    """
    Generate a current timestamp.

    Returns:
        int: The current timestamp in seconds since the epoch.
    """
    return int(time.time())

# Sync Key Declarations

class PowershellSync:
    """
    A class to represent a PowerShell key structure, with the ability to create
    a basic command structure and generate sync keys for JSON data fields.
    """

    def __init__(self, command: str = "") -> None:
        """
        Initialize the PowershellKey class with a command.

        Args:
            command (str): The PowerShell command to be executed.
        """
        self.command = command

    def create(self) -> dict[str, str]:
        """
        Creates a basic PowerShell command structure.

        Returns:
            dict[str, str]: A dictionary containing the PowerShell command structure.
        """
        struct = {
            "powershell": {
                "command": self.command
            }
        }
        return struct

    @staticmethod
    def help():
        help_msg = "powershell: runs powershell on the host. \n\tEx: powershell get-aduser bob"
        return help_msg

class CommandSync:
    """
    A class to represent a PowerShell key structure, with the ability to create
    a basic command structure and generate sync keys for JSON data fields.
    """

    def __init__(self, command: str = "") -> None:
        """
        Initialize the CommandSync class with a command.

        Args:
            command (str): The PowerShell command to be executed.
        """
        self.command = command

    def create(self) -> dict[str, str]:
        """
        Creates a basic PowerShell command structure.

        Returns:
            dict[str, str]: A dictionary containing the PowerShell command structure.
        """
        struct = {
            "command": {
                "command": self.command
            }
        }
        return struct

    @staticmethod
    def help():
        help_msg = "command: runs a command on the host, \n\tEx: command whoami /all"
        return help_msg

class SleepSync:
    """
    A sleep key
    """

    def __init__(self, time: str = "") -> None:
        """
        Initialize the PowershellKey class with a command.

        Args:
            time (str): How long to set sleep time for
        """
        self.time = time

    def create(self) -> dict[str, str]:
        """
        Creates a basic SleepSync key structure.

        Returns:
            dict[str, str]: A dictionary containing the SleepSync key
        """
        struct = {
            "sleep": {
                "time": self.time
            }
        }
        return struct

    @staticmethod
    def help():
        help_msg = "sleep: sets sleep time on the host.\n\tEx: sleep 60"
        return help_msg