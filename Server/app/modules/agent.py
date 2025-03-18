import json
import pathlib

import munch
import redis
import yaml
from modules.config import Config
from modules.log import log
from modules.redis_models import Agent, AgentData, AgentCommand
from modules.utils import generate_unique_id
from redis_om import Field, HashModel, JsonModel, get_redis_connection
import traceback
from modules.agent_script_interpreter import AgentScriptInterpreter

logger = log(__name__)


"""HUGE README:

In order to not have stale data with BaseAgent, before you call agent.data, PLEASE
call agent.load_data() to get the latest data from redis


note, register() will do this automatically
"""


class BaseAgent:
    """
    A base class that provides common functionality for all models.
    """

    def __init__(self, agent_id, config_file_path=None, **kwargs):
        # connect to redis
        self.redis_client = get_redis_connection(  # switch to config values
            host=Config().config.redis.bind.ip,
            port=Config().config.redis.bind.port,
            decode_responses=True,  # Ensures that strings are not returned as bytes
        )

        # info stuff - munch object
        self._data = munch.munchify(
            {
                "system": {
                    "hostname": None,
                    "os": None,
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
                    "new": None,  # for now, set new to true by default. May be better to set at first checkin. # agent would not show up until first checkin, so this is probably file
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
                    "command_script": None,
                },
            }
        )
        self.data.agent.id = agent_id

        # setup registry handling for certain commands
        # could make this more modular
        self.handler_registry = CommandHandlerRegistry()
        self.handler_registry.register(
            "shell whoami", GenericHandler, "system.username"
        )
        self.handler_registry.register(
            "shell hostname", GenericHandler, "system.hostname"
        )
        self.handler_registry.register("shell ver", GenericHandler, "system.os")
        self.handler_registry.register("help", HelpHandler)

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

    @data.setter
    def data(self, value):
        # Dev Note: Setting as munch object on SET, which is less common that retrieval.
        # This theoretically should be more efficent
        if not isinstance(value, munch.Munch):
            value = munch.munchify(value)
        self._data = value

    ##########
    # Script Options
    ##########

    def set_command_script(self, script_name):
        """
        Sets the command script

        """
        ## Problem here - TLDR: not getting saved to redis...

        logger.debug(f"Setting command script for {self.data.agent.id}: {script_name}")

        self.data.config.command_script = script_name
        # save newly updated data into redis
        self.unload_data()
        # self.load_data()

    def get_command_script(self):
        """
        Sets the command script

        """
        command_script = self.data.config.command_script

        logger.debug(
            f"Getting command script for {self.data.agent.id}: {command_script}"
        )

        return command_script

    ##########
    # Redis Stuff
    ##########

    def register(self):
        """
        Registers an agent in the system and ensures that the latest data is stored in Redis.
        """
        try:
            logger.info(f"Registering agent: {self.data.agent.id}")

            # Retrieve latest data from Redis before saving
            # doing this AGAIN (as well as in INIT), just incase data got changed somewhere
            # Want to be working with the latest data possible

            # bug exists here:

            try:
                stored_data = AgentData.get(self.data.agent.id)
                # logger.debug(
                #     f"Loaded existing agent data from Redis: {stored_data.json_blob}"
                # )
                self.data = json.loads(stored_data.json_blob)  # Ensure latest state

            # blanket exception, should handle this better
            except Exception as e:
                logger.critical("First connect relies on a except, works for now, FIX!")
                logger.warning(
                    f"Agent {self.data.agent.id} not found in Redis. This is expected on first check-in."
                )
                # hacky putting this here, treating this except as a proof of first connect. bad idea.
                # fine for now
                self.data.agent.new = True

            # Save the updated agent model in Redis
            agent_model = Agent(agent_id=self.data.agent.id)
            agent_model.save()

            # Unload the latest version of self.data, ensuring no loss of command_script
            self.unload_data()

        except Exception as e:
            logger.error(f"Error registering agent {self.data.agent.id}: {e}")
            logger.error(
                traceback.format_exc()
            )  # Print the full traceback for debugging
            raise e

    def unregister(self):
        """
        Deletes the agent from the system using the Agent model from `modules.redis_models`.
        The agent is identified and removed by `self.data.agent.id`.
        """
        logger.debug(f"Unregistering agent with ID: '{self.data.agent.id}'")
        # Deletion is handled by passing `self.data.agent.id` to the `redis.delete` function through `redis_om`
        Agent.delete(self.data.agent.id)

    def unload_data(self):
        """
        Store the given self.data in Redis under self.data.agent.id.
        """
        try:
            logger.debug(f"Unloading data for agent {self.data.agent.id} to redis")
            agent_data = AgentData(
                agent_id=self.data.agent.id, json_blob=json.dumps(self.data)
            )
            agent_data.save()
        except Exception as e:
            logger.error(f"Could not unload data to redis, error occured: {e}")
            raise e

    def load_data(self) -> dict:
        """
        Fetch and return the data dict from Redis by self.data.agent.id.
        """
        try:
            logger.debug(f"Loading data for agent {self.data.agent.id} from redis")
            fetched_instance = AgentData.get(self.data.agent.id)
            # JSON blob is stored as a json string in redis, need to convert back to dict
            new_dict = json.loads(fetched_instance.json_blob)
            self.data = munch.munchify(new_dict)
            return True

        except Exception as e:
            logger.error(f"Could not load data from redis, error occured: {e}")
            raise e

    #########
    # Command Queues
    ########
    # queue name should be agent id
    # need to test & rename consume_commands to return none or something on no command,
    # so a "no command" state can be implemented.

    # NOTE! queue is right to left
    # POP <-- item1 <-- item2 <-- item3 <-- push

    # chagne to command ID
    def enqueue_command(self, command):
        """
        Adds a command (string) to the Redis list (queue).

        returns command ID
        """
        try:

            command_id = generate_unique_id()

            # what's the key for this...?
            logger.debug(f"Enqueing command: '{command_id}'")
            self.redis_client.rpush(self.data.agent.id, command_id)
            self._store_command(command=command, command_id=command_id)
            return command_id

        except Exception as e:
            logger.error(e)
            raise e

    def dequeue_command(self):
        """
        Pops a command ID from the Redis queue and retrieves the full command.

        Returns:
            - command (str) if found
            - False if no command exists
        """
        try:
            logger.debug("Dequeuing command id")

            # Pop the command_id from Redis queue
            command_id = self.redis_client.lpop(self.data.agent.id)

            if not command_id:
                return False  # No command in queue

            # Retrieve the full command object from Redis OM
            command_obj = AgentCommand.get(command_id)

            if not command_obj:
                logger.warning(
                    f"Command ID {command_id} not found in AgentCommand store."
                )
                return False

            print(f"Dequeued Command: {command_obj.command}")

            return command_obj  # Return the command object

        except Exception as e:
            logger.error(f"Dequeue command error: {e}")
            raise e

    def get_all_commands_and_responses(self):
        """
        Gets all commands and responses for a specific agent.

        Returns:
            List of dictionaries with command_id, command, and response.
        """
        try:
            logger.debug(f"Fetching all commands for agent {self.data.agent.id}")

            # Construct key pattern (assuming the storage format follows `whispernet:agent:command:<command_id>`)
            key_pattern = f"whispernet:agent:command:*"

            # Use SCAN to iterate over matching keys
            command_keys = list(self.redis_client.scan_iter(key_pattern))

            result = []
            for key in command_keys:
                command_obj = AgentCommand.get(
                    key.split(":")[-1]
                )  # Extract ID from key

                # basically just check that the agent id matches the current agent id before returning the commands.
                if command_obj and command_obj.agent_id == self.data.agent.id:
                    result.append(
                        {
                            "command_id": command_obj.command_id,
                            "command": command_obj.command,
                            "response": (
                                command_obj.response if command_obj.response else None
                            ),
                            "timestamp": command_obj.timestamp,
                        }
                    )

            return result

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e

    def get_one_command_and_response(self, command_id):
        """
        Gets a single command and its response based on the provided key.

        Args:
            command_id (str): The Redis key for the command (e.g., "whispernet:agent:command:<command_id>")

        Returns:
            A dictionary with command_id, command, response, and timestamp if the agent ID matches,
            otherwise None.
        """
        try:
            logger.debug(
                f"Fetching command for agent {self.data.agent.id} with key {command_id}"
            )

            # Extract the command ID from the key (assumes key is in the format: whispernet:agent:command:<command_id>)
            # command_id = key.split(":")[-1]

            command_obj = AgentCommand.get(command_id)

            # Check if the command exists and if its agent_id matches the current agent's id
            if command_obj and command_obj.agent_id == self.data.agent.id:
                return {
                    "command_id": command_obj.command_id,
                    "command": command_obj.command,
                    "response": command_obj.response if command_obj.response else None,
                    "timestamp": command_obj.timestamp,
                }

            # Return None if there's no match or the command doesn't exist
            return None

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e

    def _store_command(self, command_id, command):
        """
        Store command key

        INTERNAL METHOD - shuold be caled from enqueue_command, as that generates the UUID for you

        """
        try:

            ac = AgentCommand(
                command_id=command_id,
                command=command,
                agent_id=self.data.agent.id,
                response="",
            )

            ac.save()
        except Exception as e:
            logger.error(e)
            raise e

    def store_response(self, command_id, response):
        """
        Stores response for a command.
        Finds the command by command_id and updates the response field.
        """
        try:
            # Retrieve the command entry by ID
            command_entry = AgentCommand.get(command_id)
            agent_id = self.data.agent.id

            if not command_entry:
                logger.error(f"Command ID {command_id} not found.")
                return False  # Command not found

            # Update the response field
            command_entry.response = response
            command_entry.save()  # Save back to Redis

            # Use handler if one is registered
            # ex, help command
            handler = self.handler_registry.get_handler(command_entry.command)
            if handler:
                handler.store(command_entry=command_entry, agent_id=agent_id)
            else:
                print(f"No custom handler found for {command_entry.command}")

            logger.debug(f"Response stored for Command ID {command_id}")
            return True  # Successfully updated

        except Exception as e:
            logger.error(f"Error storing response for Command ID {command_id}: {e}")
            raise e

    ##########
    # Update some data methods
    # Better than direct access, start implementing these for common fields.
    # helps enforcing types as well
    ##########
    def update_notes(self, notes):
        """
        Updates notes field in data

        """
        try:
            if notes == None:
                logger.warning(f"Notes being updated for {self.data.agent.id} are None")
            logger.debug(f"Updating notes: {notes}")
            self.data.agent.notes = notes
            # dump data
            self.unload_data()

        except Exception as e:
            logger.error(f"Error updating notes field: {e}")

    def update_new_status(self, new: bool):
        """
        Updates notes field in data
        """
        try:
            logger.debug(f"Updating new status: {new}")
            self.data.agent.new = new
            # dump data
            self.unload_data()

        except Exception as e:
            logger.error(f"Error updating new status field: {e}")


## command registry stuff
# TLDR: Allows for custom handling to each command that is registered, in order to record outputs
# Downsides, only catches command AFTER it's run, not really a way to catch it before at the moment


class BaseCommandHandler:
    def store(self, command_entry):
        raise NotImplementedError("Store method not implemented")


class CommandHandlerRegistry:
    def __init__(self):
        self.handlers = {}

    def register(self, command_pattern, handler_class, *args, **kwargs):
        """
        Register a handler with optional arguments.
        """
        # Store handler with additional args and kwargs
        self.handlers[command_pattern] = (handler_class, args, kwargs)

    def get_handler(self, command):
        """
        Retrieve the handler for a given command.
        """
        for pattern, (handler_class, args, kwargs) in self.handlers.items():
            if pattern in command:
                # Instantiate the handler with stored args and kwargs
                return handler_class(*args, **kwargs)
        return None


class GenericHandler(BaseCommandHandler):
    """
    Generic handler for dynamically storing command responses at specified locations
    within the agent's data structure.

    This handler is designed to be highly flexible and reusable for a wide range of commands.
    It allows for dynamic storage by specifying the `save_location` during registration,
    which determines where the response will be saved within the agent's "data" structure

    **How It Works:**
        - The `save_location` is passed as a dot-notated string (e.g., "system.hostname", "network.internal_ip").
        - This string is split by dots and traversed to locate or create the target field.
        - If any nested attribute doesn't exist, it is dynamically initialized as a `Munch()` object.
        - The command response is then stored at the specified location.
        - The updated data is saved back to Redis using `agent.unload_data()`.

    **Example Registration:**
        self.handler_registry.register("shell hostname", GenericHandler, save_location="system.hostname")
        self.handler_registry.register("shell whoami", GenericHandler, save_location="system.username")
        self.handler_registry.register("shell ver", GenericHandler, save_location="system.os_version")

    **Example Save Locations:**
        - "system.hostname" → Saves the response under `agent.data.system.hostname`
        - "network.internal_ip" → Saves the response under `agent.data.network.internal_ip`
        - "geo.country" → Saves the response under `agent.data.geo.country`
        (On the web gui, this is rendered in the MAIN tab for each agent)

    **Note:**
        - This handler directly updates the data field in the agent entry in Redis.
        - It is designed to be idempotent, preventing duplicate entries by overwriting existing values.
        - If the `save_location` is invalid or not reachable, the handler gracefully logs the issue and returns False.
    """

    def __init__(self, save_location):
        """
        Initialize with a save location for dynamic storage.

        Args:
            save_location (str): Dot-notated string specifying where to store the response.
                                Example: "system.hostname" or "network.internal_ip"
        """
        self.save_location = save_location  # Store as an instance variable

    def store(self, command_entry, agent_id):
        """
        Generic processing and storing for any command response.

        This method:
            - Loads the latest agent data from Redis.
            - Traverses the save_location, creating nested keys if needed.
            - Stores the command response at the specified location.
            - Saves the updated data back to Redis.

        Args:
            command_entry (AgentCommand): The command entry containing the response to be stored.
            agent_id (str): The unique ID of the agent that executed the command.

        Returns:
            bool: True if the response is successfully stored, False otherwise.
        """
        try:
            # Load the latest agent data
            agent = BaseAgent(agent_id)
            agent.load_data()

            # Split the save_location by dots to support nested attributes
            location_parts = self.save_location.split(".")
            target = agent.data

            # Traverse the nested attributes, creating them if they don't exist
            for part in location_parts[:-1]:
                if not hasattr(target, part) or getattr(target, part) is None:
                    setattr(target, part, munch.Munch())
                target = getattr(target, part)

            # Set the value at the final attribute
            setattr(target, location_parts[-1], command_entry.response)
            agent.unload_data()

            logger.info(
                f"Stored '{command_entry.response}' at '{self.save_location}' for Agent ID {agent_id}"
            )
            return True

        except (AttributeError, Exception) as e:
            logger.error(
                f"Error storing at '{self.save_location}' for Agent ID {agent_id}: {e}"
            )
            return False

        except (AttributeError, Exception) as e:
            logger.error(
                f"Error storing at '{self.save_location}' for Agent ID {agent_id}: {e}"
            )
            return False


# any handlers that need *specific* stuff, otherwise generic handler stores in the
# data of each agent


class HelpHandler(BaseCommandHandler):
    """
    Custom handler for help command, which appends the contents of the current script with it

    Ex:
        > File Command
            ...

        > Extension Script `somescript.yaml` options:
            ...

        This help string is pulled directly from the currently seelcted .yaml script,
        and is generated by the AgentScriptInterpreter's extract_help_info() method


        Note: This does directly update the response string in redis.
    """

    def store(self, command_entry, agent_id):
        """
        Custom processing and storing for 'help' command response.
        """
        try:
            # Load the latest agent data
            agent = BaseAgent(agent_id)
            agent.load_data()

            # Get the help string
            asi = AgentScriptInterpreter(
                script_name=agent.data.config.command_script, agent_id=agent_id
            )
            extension_help_string = asi.extract_help_info()

            # Get command id and current response
            command_id = command_entry.command_id
            current_response = command_entry.response

            # Check if the extension string is already appended
            if extension_help_string not in current_response:
                # Append only if not already present
                command_entry.response += extension_help_string
                # Save/update the response in Redis
                agent.store_response(command_id, command_entry.response)

            logger.debug(f"Help response updated for Command ID {command_id}")

        except (AttributeError, Exception) as e:
            logger.error(f"Error for Agent ID {agent_id}: {e}")
            return False
