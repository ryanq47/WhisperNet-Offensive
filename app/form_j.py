import munch
import json
from modules.log import log
from sync_powershell import FormJPowershell

logger = log(__name__)


# list of sync_key handlers
handlers = {"Powershell": FormJPowershell}  # self.handle_client_name,


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


if __name__ == "__main__":
    ex_request = {
        "rid": "unique_request_identifier",
        "timestamp": 1710442988,
        "status": "success",
        "data": {
            "Powershell": [
                {
                    "executable": "ps.exe",
                    "command": "net user /domain add bob",
                    "id": 1234,
                },
                {
                    "executable": "ps.exe",
                    "command": "net group /add Domain Admins Bob",
                    "id": 1235,
                },
            ],
        },
        "error": None,
    }

    ex_request_json = json.dumps(ex_request)

    c = FormJ(str(ex_request_json))
    result = c.parse()
    print("parsed values:")
    for i in result:
        print(f"[+] {i}")

    c.process()
