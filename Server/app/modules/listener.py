import json
import pathlib

import munch
import redis
import yaml
from modules.config import Config
from modules.log import log
from modules.redis_models import Listener
from redis_om import Field, HashModel, JsonModel, get_redis_connection

logger = log(__name__)


class BaseListener:
    """
    A base class that provides common functionality for all models.
    """

    def __init__(self, listener_id, **kwargs):
        # connect to redis
        self.redis_client = get_redis_connection(  # switch to config values
            host=Config().config.redis.bind.ip,
            port=Config().config.redis.bind.port,
            decode_responses=True,  # Ensures that strings are not returned as bytes
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

        # may or may not be needed
        self.alias = None
        self.template = None

        # info stuff - munch object
        self._data = munch.munchify(
            {
                "listener": {
                    "name": None,  # Unique name for the listener
                    "id": None,  # UUID for listener
                },
                "network": {
                    "address": None,  # IP address to bind (e.g., "0.0.0.0" for all interfaces)
                    "port": None,  # Port number to listen on
                    "protocol": None,  # Protocol (e.g., "TCP", "UDP")
                },
                "endpoints": [  # List of endpoints for different functionalities
                    {
                        "endpoint_name": "command",
                        "path": "/command",
                        "methods": ["POST", "GET"],
                    },
                    {
                        "endpoint_name": "heartbeat",
                        "path": "/heartbeat",
                        "methods": ["POST"],
                    },
                ],
                "ssl": {
                    "ssl_enabled": False,  # Whether SSL is enabled
                    "ssl_cert_path": None,  # Path to SSL certificate (if SSL is enabled)
                    "ssl_key_path": None,  # Path to SSL key (if SSL is enabled)
                },
                "authentication": {  # Authentication settings
                    "enabled": True,  # Whether authentication is required
                    "token": "securetoken123",  # Authentication token or mechanism
                },
                "metadata": {  # Additional metadata
                    "created_at": None,
                    "updated_at": None,
                    "version": None,
                },
            }
        )

        # Load data from Redis if agent_id is provided
        if self.data.listener.id:
            self._load_data_from_redis(self.data.listener.id)

    def _load_data_from_redis(self, listener_id):
        """Internal: Load client data from Redis."""
        try:
            # get data from redis
            data = self.redis_client.get(f"client:{self.data.listener.id}")
            if data:
                self._data = munch.munchify(json.loads(data))
                logger.debug(
                    f"Loaded client data for {self.data.listener.id} from Redis."
                )
            else:
                logger.debug(
                    f"No data found in Redis for client: {self.data.listener.id}"
                )
                # call register
        except Exception as e:
            logger.error(f"Error loading data from Redis: {e}")
            raise e

    @property
    def data(self):
        """
        Munch Object of data


        Access with dot notation:
            ex: obj.data.system.hostname = somehostname


        Dev Note:
            This function exists so there's function hints when you hover over the object/property
        """
        return self._data

    def to_dict(self):
        """Convert the model's attributes to a dictionary."""
        return {key: getattr(self, key) for key in vars(self)}

    def to_json(self):
        """Convert the model to a JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        """Create an instance from a dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_data):
        """Create an instance from a JSON string."""
        return cls.from_dict(json.loads(json_data))

    ##########
    # Script Options
    ##########
    def load_config(self, config_file_path: str | pathlib.Path):
        """
        Load template file into current session.

        config_file_path (str | pathlib.path ): Path to config

        """
        try:  # make bulletproof
            # Load configuration from a script if provided
            # logger.debug(f"Loading script file: {template_file_path}")
            with open(config_file_path, "r") as file:
                data = yaml.safe_load(file)

            # not doing anything with config at the moment

        except FileNotFoundError as fnfe:
            logger.error(f"Configuration file not found: {config_file_path}")
            logger.error(fnfe)
            raise fnfe

        except Exception as e:
            logger.error(e)
            raise e

    @staticmethod
    def validate_config(config_file_path: str | pathlib.Path):
        """
        Validates a config file

        returns True on success, false on fail
        """
        try:
            with open(config_file_path, "r") as file:
                data = yaml.safe_load(file)

            # maybe use
            template_dict = data.get("template", None)
            alias_dict = data.get("alias", None)
            info_dict = data.get("info", None)

            if template_dict is None:
                # err
                logger.error("Missing 'template' section in configuration.")
                return False
                # raise ValueError("Configuration must include a 'template' section.")

            if alias_dict is None:
                # err
                logger.error("Missing 'alias' section in configuration.")
                return False
                # raise ValueError("Configuration must include an 'alias' section.")

            if info_dict is None:
                # warning
                logger.warning("Missing 'info' section in configuration")

            return True

        except FileNotFoundError as fnfe:
            logger.error(f"Configuration file not found: {config_file_path}")
            logger.error(fnfe)
            raise fnfe

        except Exception as e:
            logger.error("An error not related to the config file contents occured:")
            logger.error(e)
            raise e

    ##########
    # Redis Stuff
    ##########

    def register(self):
        """
        Registers a client to ...
            - redis?

        Can be whatever we need

        """
        # self.redis

        # set self.registered to true?

        # redis con setup...

        # redis model ...

        # redis save...
        logger.info(f"Registering listener: {self.data.listener.id}")

        listener_model = Listener(
            agent_id=self.data.listener.id, name=self.data.listener.name
        )
        listener_model.save()
        # change to listener agent

    def unregister(self):
        """
        Unregister the client
        """
        ...

    def load_data(self):
        """
        Loads data from redis.
        """
        # create a redis model for this

        # have it be created at register

        # this class is meant to load from redis after/on checkin, to re create the class

        # might be able to pull off in the init as well
        ...

    def unload_data(self):
        """
        Unload data to redis
        """
        ...

    ##########
    # User STuff
    ##########

    # for HTTP if ever wanted
    # def config_register_endpoint(self, name, endpoint, methods=None):
    #     """
    #     REgister and endpoint to the config.

    #     Basically, this just makes it easier to do/a one stop shop
    #     """

    #     # get endpoint
    #     # add new entry to data.endpoints list

    #     methods = {
    #         # list comp of methods?
    #         ...
    #     }

    #     new_entry = {
    #         "endpoint_name": name,
    #         "path": endpoint,  # do some processingon this so it's correct
    #         "methods": methods,  # onyl add methods if methods? may not apply to pure tcp
    #     }

    # def config_deregister_endpoint(self, endpoint):
    #     """
    #     deregister and endpoint to the config

    #     Basically, this just makes it easier to do/a one stop shop
    #     """
    #     ...


# ## Basic example of usage
# client = Client()
# ## load config - NEEDS to be called first
# client.load_config(config_file_path="example.yaml")

# ## make sure to run this every time before command gets sent off
# ## LOG the before & after as well, in action log or something
# client.format_command(command="powershell", arguments="whoami")

# print(client.validate_config(config_file_path="example.yaml"))

# access data in the data model
# Categories:
#  - system
#  - network
#  - hardware
#  - agent
#  - security
#  - geo

# client.data.system.os = "SOMEOS"
# client_os = client.data.system.os
# print(client.data.system.os) or print(client_os)

# if you want to do custom options you can too:
# client.data.system.second_os = "SOMEOS2"
# print(client.data.system.second_os)

# # ## Basic example of usage
# client = Client()
# # ## load config - NEEDS to be called first
# client.load_config(config_file_path="example.yaml")

# # ## make sure to run this every time before command gets sent off
# # ## LOG the before & after as well, in action log or something
# client.format_command(command="powershell", arguments="whoami")

# print(client.validate_config(config_file_path="example.yaml"))
# client.data.system.os = "SOMEOS"
# print(client.data.system.os)

# client.data.system.urmom = "SOMEOS2"
# print(client.data.system.urmom)
