import json
import pathlib

import munch
import redis
import yaml
from modules.config import Config
from modules.log import log
from modules.redis_models import Listener, ListenerData
from modules.utils import generate_mashed_name, generate_unique_id
from redis_om import Field, HashModel, JsonModel, get_redis_connection

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = log(__name__)


# future idea... as listeners are different, baseHttpListener? BaseTcpListener?
class BaseListener:
    """
    A base class that provides common functionality for listeners.
    """

    def __init__(self, host, name, port, listener_id=None, **kwargs):
        # connect to redis
        self.redis_client = get_redis_connection(  # switch to config values
            host=Config().config.redis.bind.ip,
            port=Config().config.redis.bind.port,
            decode_responses=True,  # Ensures that strings are not returned as bytes
        )

        # info stuff - munch object
        self._data = munch.munchify(
            {
                "listener": {
                    "name": None,  # Unique name for the listener
                    "id": None,  # UUID for listener
                    "pid": None,
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

        # get the data in at init, makes this much easier to do other things
        self.data.network.port = port
        self.data.network.address = host
        self.data.listener.name = name

        # if a listener ID is not specified, this means that we want a full new listener.
        if listener_id == None:
            uuid = generate_unique_id()
            logger.warning(f"No listener ID provided, settings as: {uuid}")
            self.data.listener.id = uuid  ## UUID generate
            # auto register and stuff
            self.register()

        # if a listener ID is specified, it is assumed the listener already exists, or is being re-spawned
        # We don't call load_data, as that tries to get it from redis, which may be empty,
        # so we just register it as normal, and let that handle the redis and DB insertion (sqliteDB will not insert if listener id exists in it)
        # see listenerstore.add_listener
        # A better way in the future to handle this may be a "respawn" arg (bool)
        else:
            self.data.listener.id = listener_id
            self.register()

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
        Registers a listener to ...
            - redis?

        Can be whatever we need

        """
        logger.info(f"Registering listener: {self.data.listener.id}")

        # Check if name is provided
        if self.data.listener.name == None:
            name = generate_mashed_name()
            logger.warning(f"No name provided, setting as '{name}'")
            self.data.listener.name = name

        listener_model = Listener(
            listener_id=self.data.listener.id, name=self.data.listener.name
        )
        # logger.debug("SAVING LISTENER MODEL")
        listener_model.save()
        self.unload_data()

        # save to sqlitedb:
        listener_store = ListenerStore()
        listener_store.add_listener(
            id=self.data.listener.id,
            port=self.data.network.port,
            address=self.data.network.address,
            name=self.data.listener.name,
            type="http",  # Figure out type later, hardcoding for now as we only have one type
        )

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

        # delete from sqlitedb
        listener_store = ListenerStore()
        listener_store.delete_listener(self.data.listener.id)

    def unload_data(self):
        """
        Store the given self.data in Redis under self.data.agent.id.
        """
        try:
            logger.debug(
                f"Unloading data for listener {self.data.listener.id} to redis"
            )
            listener_data = ListenerData(
                listener_id=self.data.listener.id, json_blob=json.dumps(self.data)
            )
            listener_data.save()
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

            fetched_instance = ListenerData.get(self.data.listener.id)
            # JSON blob is stored as a json string in redis, need to convert back to dict
            new_dict = json.loads(fetched_instance.json_blob)

            # set self_data back to munched data.
            self._data = munch.munchify(new_dict)

            return True

        except Exception as e:
            logger.error(f"Could not load data from redis, error occurred: {e}")
            raise e


# Create the base for model declarations
Base = declarative_base()


# Define the Listener model using the provided definition
class ListenerStoreModel(Base):
    __tablename__ = "listeners"

    name = Column(String, nullable=False)  # listener's name
    id = Column(String, primary_key=True)  # primary key, allowing duplicate names
    port = Column(Integer, nullable=False)  # listening port
    address = Column(String, nullable=False)  # listening address
    type = Column(String, nullable=False)


class ListenerStore:
    """
    A class to manage listener entries using SQLAlchemy and SQLite.

    Attributes:
        engine: SQLAlchemy engine for connecting to the SQLite database.
        session: SQLAlchemy session for performing database operations.
    """

    def __init__(self):
        """
        Initializes the ListenerStore instance.

        - Creates a SQLite database connection.
        - Creates the listeners table if it doesn't already exist.
        - Initializes a SQLAlchemy session for database operations.
        """
        self.engine = create_engine(
            "sqlite:///app/instance/listeners.db", echo=False
        )  # flip echo on for the queries
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_listener(self, name, id, port, address, type):
        """
        Adds a new listener to the database if it does not already exist.

        Args:
            name (str): The name of the listener.
            id (str): Unique identifier for the listener.
            port (int): The port number on which the listener is active.
            address (str): The address on which the listener is active.
            type (str): The type of the listener.
        """
        # Check if a listener with the same id already exists
        existing_listener = (
            self.session.query(ListenerStoreModel).filter_by(id=id).first()
        )
        if existing_listener:
            logger.info(f"Listener with id {id} already exists. Skipping insertion.")
            return

        new_listener = ListenerStoreModel(
            name=name,
            id=id,
            port=port,
            address=address,
            type=type,
        )
        self.session.add(new_listener)
        self.session.commit()

    def get_all_listeners(self):
        """
        Retrieves all listeners from the database.

        Returns:
            list: A list of Listener objects.
        """
        return self.session.query(ListenerStoreModel).all()

    def get_listener(self, uuid):
        """
        Retrieves a single listener by its UUID.

        Args:
            uuid (str): The UUID of the listener to retrieve.

        Returns:
            Listener: The Listener object if found, otherwise None.
        """
        return self.session.query(ListenerStoreModel).filter_by(uuid=uuid).first()

    def delete_listener(self, uuid):
        """
        Deletes a listener from the database by its UUID.

        Args:
            uuid (str): The UUID of the listener to delete.
        """
        listener = self.session.query(ListenerStoreModel).filter_by(uuid=uuid).first()
        if listener:
            self.session.delete(listener)
            self.session.commit()
