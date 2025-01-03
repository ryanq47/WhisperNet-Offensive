import json
import pathlib

import munch
import redis
import yaml
from modules.config import Config
from modules.log import log
from modules.redis_models import Agent
from redis_om import Field, HashModel, JsonModel, get_redis_connection

logger = log(__name__)


class BaseAgent:
    """
    A base class that provides common functionality for all models.
    """

    def __init__(self, agent_id, **kwargs):
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
                "system": {
                    "hostname": None,
                    "os": None,
                    "os_version": None,
                    "architecture": None,
                    "username": None,
                    "privileges": None,
                    "uptime": None,
                },
                "network": {
                    "internal_ip": None,
                    "external_ip": None,
                    "mac_address": None,
                    "default_gateway": None,
                    "dns_servers": [],
                    "domain": None,
                },
                "hardware": {
                    "cpu": None,  # could get with the one assembly command to get that info - would be quiet.
                    "cpu_cores": None,
                    "ram": None,
                    "disk_space": None,
                },
                "agent": {
                    "id": agent_id,
                    "version": None,
                    "first_seen": None,
                    "last_seen": None,
                },
                "security": {
                    "av_installed": [],
                    "firewall_status": None,
                    "sandbox_detected": False,
                    "debugger_detected": False,
                },
                "geo": {
                    "country": None,
                    "city": None,
                    "latitude": None,
                    "longitude": None,
                },
                "config": {
                    "file": None,  # config file
                },
            }
        )

        # Load data from Redis if agent_id is provided
        if self.data.agent.id:
            self._load_data_from_redis(self.data.agent.id)

    def _load_data_from_redis(self, agent_id):
        """Internal: Load agent data from Redis."""
        try:
            # get data from redis
            data = self.redis_client.get(f"agent:{self.data.agent.id}")
            if data:
                self._data = munch.munchify(json.loads(data))
                logger.debug(f"Loaded agent data for {self.data.agent.id} from Redis.")
            else:
                logger.debug(f"No data found in Redis for agent: {self.data.agent.id}")
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

            # maybe use
            template_dict = data.get("template", None)
            alias_dict = data.get("alias", None)

            if template_dict is None:
                logger.error("Missing 'template' section in configuration.")
                raise ValueError("Configuration must include a 'template' section.")

            if alias_dict is None:
                logger.error("Missing 'alias' section in configuration.")
                raise ValueError("Configuration must include an 'alias' section.")

            # load in specific items from config file
            self._load_alias(alias_dict)
            self._load_template(template_dict)
            # self.loaded = True # a check to make sure this happens?

            # Next...
            # loop over each key and
            # >  parse and add alias to valid commands (user sees these)
            # >  parse add template to template settings/however those are handled
        except FileNotFoundError as fnfe:
            logger.error(f"Configuration file not found: {config_file_path}")
            logger.error(fnfe)
            raise fnfe

        except Exception as e:
            logger.error(e)
            raise e

    def _load_alias(self, alias_dict: dict):
        """
        Internal
        Loads alias into agent.

        Seperate method for future handling/standard way of handling
        """
        try:
            # munchify the dicts for better/easier access
            self.alias = munch.munchify(alias_dict)

            logger.debug("alias:")
            # .keys: keys
            # .values: values
            # .items: key, value pair
            for key, val in self.alias.items():
                logger.debug(f"\t{key}: {val}")

        except Exception as e:
            logger.error(e)
            raise e

    def _load_template(self, template_dict: dict):
        """
        Internal
        Loads alias into agent.

        Seperate method for future handling/standard way of handling

        """
        try:
            # munchify the dicts for better/easier access
            self.template = munch.munchify(template_dict)

            logger.debug("template:")
            # .keys: keys
            # .values: values
            # .items: key, value pair
            for key, val in self.template.items():
                logger.debug(f"\t{key}: {val}")

        except Exception as e:
            logger.error(e)
            raise e

    def format_command(self, command: str, arguments: str):
        """
        Auto format a command based on its template string

        command (str): The command. Used for lookups in config.yaml

        arguments (str): The arguments


        Returns: Formatted command

        Ex:

        powershell iex bypass; powershell %%COMMAND%% (from config file)
        into
        powershell iex bypass; powershell whoami

        NOTE:
            If arguments/vars are ever implemented, this would need some adjustment.

            (maybe as kwargs/args, then iter, and positional?)
        """
        try:

            # Get the template based on which command
            command_template = self.template.get(command, None)
            if not command_template:
                logger.error(f"Command template for '{command}' not found")
                return

            # Replace %%COMMAND%% with the provided arguments
            formatted_command = command_template.replace("%%COMMAND%%", arguments)
            logger.debug(formatted_command)

            return formatted_command

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
        Registers an agent to  redis

        """
        logger.info(f"Registering agent: {self.data.agent.id}")

        agent_model = Agent(agent_id=self.data.agent.id)
        agent_model.save()

    def unregister(self):
        """
        Unregister the agent
        """
        logger.debug(f"Unregistering agent with ID:'{self.data.agent.id}'")
        # not the most clear, but this takes in (I think) the prim key, and then deletes the entry based on it
        # It seems to be passed directly to the redis.delete function through redis_om
        Agent.delete(self.data.agent.id)

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

    #########
    # Command Queues
    ########
    # queue name should be agent id
    # need to test & rename consume_commands to return none or something on no command,
    # so a "no command" state can be implemented.

    # NOTE! queue is right to left
    # POP <-- item1 <-- item2 <-- item3 <-- push

    def enqueue_command(self, command: str):  # , queue_name: str = "c2_queue"):
        """
        Adds a command (string) to the Redis list (queue).
        """
        logger.debug(f"Enqueing command: '{command}'")
        self.redis_client.rpush(self.data.agent.id, command)

    def dequeue_command(self):  # queue_name: str = "c2_queue"):
        """
        Continuously pops commands off the queue from the left side (head).


        if a command exists, returns the command (str), else returns False (bool)

        """
        # while True:
        # BLPOP returns a tuple: (queue_name, command)
        # It blocks until a value is available.

        # changed up to if not a command, reutrn false
        result = self.redis_client.blpop(self.data.agent.id)

        if result:
            queue, command = result
            # queue == b'c2_queue' (bytes)
            # command == b'list_system_users' (bytes)
            command_str = command  # .decode("utf-8")
            logger.debug(f"dequed command: {command_str}")
            return command_str
            # Process the command
            # ...
        else:
            return False


# ## Basic example of usage
# agent = Agent()
# ## load config - NEEDS to be called first
# agent.load_config(config_file_path="example.yaml")

# ## make sure to run this every time before command gets sent off
# ## LOG the before & after as well, in action log or something
# agent.format_command(command="powershell", arguments="whoami")

# print(agent.validate_config(config_file_path="example.yaml"))

# access data in the data model
# Categories:
#  - system
#  - network
#  - hardware
#  - agent
#  - security
#  - geo

# agent.data.system.os = "SOMEOS"
# client_os = agent.data.system.os
# print(agent.data.system.os) or print(client_os)

# if you want to do custom options you can too:
# agent.data.system.second_os = "SOMEOS2"
# print(agent.data.system.second_os)

# # ## Basic example of usage
# agent = Agent()
# # ## load config - NEEDS to be called first
# agent.load_config(config_file_path="example.yaml")

# # ## make sure to run this every time before command gets sent off
# # ## LOG the before & after as well, in action log or something
# agent.format_command(command="powershell", arguments="whoami")

# print(agent.validate_config(config_file_path="example.yaml"))
# agent.data.system.os = "SOMEOS"
# print(agent.data.system.os)

# agent.data.system.urmom = "SOMEOS2"
# print(agent.data.system.urmom)

"""
Then like

comamnd comes in,         gets intercepted by model, parsed, and adjusted dynamically as needed based on config?
exec:powershell whoami ->  ...                               exec:powershell -c -noUAC "whoami"

makes it easier for the user, however a tad bit less transparent on what's happening under the hood

Shortcomings: still need to find out how to call this, other than popen or something.
"""
