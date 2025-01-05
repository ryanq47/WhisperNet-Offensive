import json
import pathlib

import munch
import redis
import yaml
from modules.config import Config
from modules.log import log
from modules.redis_models import Listener
from modules.utils import generate_mashed_name, generate_unique_id
from redis_om import Field, HashModel, JsonModel, get_redis_connection

logger = log(__name__)


# future idea... as listeners are different, baseHttpListener? BaseTcpListener?
class BaseListener:
    """
    A base class that provides common functionality for listeners.
    """

    def __init__(self, listener_id=None, **kwargs):
        # connect to redis
        self.redis_client = get_redis_connection(  # switch to config values
            host=Config().config.redis.bind.ip,
            port=Config().config.redis.bind.port,
            decode_responses=True,  # Ensures that strings are not returned as bytes
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

        # may or may not be needed
        # self.alias = None
        # self.template = None

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
                "metadata": {  # Additional metadata
                    "created_at": None,
                    "updated_at": None,
                    "version": None,
                },
            }
        )

        if listener_id == None:
            uuid = generate_unique_id()
            logger.warning(f"No listener ID provided, settings as: {uuid}")
            self.data.listener.id = uuid  ## UUID generate

        # Check if name is provided
        if self.data.listener.name == None:
            name = generate_mashed_name()
            logger.warning(f"No name provided, setting as '{name}'")
            self.data.listener.name = name

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

    ##########
    # Redis Stuff
    ##########

    def register(self):
        """
        Registers a client to ...
            - redis?

        Can be whatever we need

        """
        logger.info(f"Registering listener: {self.data.listener.id}")

        listener_model = Listener(
            listener_id=self.data.listener.id, name=self.data.listener.name
        )
        listener_model.save()
        # change to listener agent

    def unregister(self):
        """
        Unregister the client
        """
        logger.debug(
            f"Unregistering listener '{self.data.listener.name}', with ID:'{self.data.listener.id}'"
        )
        # not the most clear, but this takes in (I think) the prim key, and then deletes the entry based on it
        # It seems to be passed directly to the redis.delete function through redis_om
        Listener.delete(self.data.listener.id)

    def unload_data(self):
        """
        Store the given self.data in Redis under self.data.agent.id.
        """
        try:
            logger.debug(
                f"Unloading data for listener {self.data.listener.id} to redis"
            )
            # agent_data = AgentData(
            #     agent_id=self.data.agent.id, json_blob=json.dumps(self.data)
            # )
            # agent_data.save()
        except Exception as e:
            logger.error(f"Could not unload data to redis, error occurred: {e}")
            raise e

    def load_data(self) -> dict:
        """
        Fetch and return the data dict from Redis by self.data.agent.id.
        """
        try:
            logger.debug(
                f"Loading data for listener {self.data.listener.id} from redis"
            )
            # fetched_instance = AgentData.get(self.data.agent.id)
            ## JSON blob is stored as a json string in redis, need to convert back to dict
            # new_dict = json.loads(fetched_instance.json_blob)
            # self.data = new_dict
            return True

        except Exception as e:
            logger.error(f"Could not load data from redis, error occurred: {e}")
            raise e

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
