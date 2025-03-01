from abc import ABC, abstractmethod
import time
import importlib.util
import inspect
import os
from modules.log import log
import pathlib
from modules.config import Config


logger = log(__name__)


class BaseCommand(ABC):
    def __init__(self, args, args_list, agent_id):
        self.args = args

    # abstract makes sure the subclass implements this
    @abstractmethod
    def run(self):
        """Execute the command."""
        pass

    def set_sleep(self, duration=10):
        """Optionally sleep before or after command execution."""
        time.sleep(duration)


class CommandFactory:
    def __init__(self):
        self.commands = {}

    # def load_command_module(self, module):
    #     self._register_commands_from_module(module)

    def register_commands_from_module(self, module):
        # Iterate through all classes defined in the module
        for name, cls in inspect.getmembers(module, inspect.isclass):
            # Check if the class is a subclass of BaseCommand (but not BaseCommand itself)
            if issubclass(cls, BaseCommand) and cls is not BaseCommand:
                # Check for the required command_name attribute
                if hasattr(cls, "command_name"):
                    command_name = getattr(cls, "command_name")
                    self.commands[command_name] = cls
                    print(f"Registered command: {command_name}")
                else:
                    print(f"Warning: {name} does not define a command_name attribute")

    # inits the class for us
    def create_command(self, command_name, args_list, agent_id):
        command_cls = self.commands.get(command_name)
        # if passed in command not in script (or not registered/loaded correctly)
        if command_cls is None:
            raise ValueError(f"Command '{command_name}' is not registered")
        return command_cls(command_name, args_list, agent_id)


class AgentScriptInterpreter:
    def __init__(self, script_name: str, agent_id):
        """
        Initializes the script interpreter with the given script name.
        Loads and parses the YAML script.
        """
        if not script_name:
            raise ValueError("Cannot have a blank script name.")
        if not agent_id:
            raise ValueError("Cannot have a blank agent_id.")

        self.script_name = script_name
        self.agent_id = agent_id

        # Load script path - replace me with a dynamic import
        self.root_project_path = pathlib.Path(Config().root_project_path)
        self.script_path = (
            self.root_project_path / "data" / "scripts" / self.script_name
        )
        module_name = self.script_name.split(".")[
            0
        ]  # e.g., 'script1' from 'script1.py'
        script_path_str = str(self.script_path)

        spec = importlib.util.spec_from_file_location(module_name, script_path_str)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        logger.debug(f"Script Path: {self.script_path}")

        # run commandfactory, to get the valid comamnds
        self.command_factory = CommandFactory()
        self.command_factory.register_commands_from_module(module)

    def process_command(self, inbound_command):
        """
        Processes the given command from the script.
        If found, returns a list of full command strings to enqueue.
        If not found, logs an error and returns False.

        inbound_command: The FULL inbound command, ex "ping 127.0.0.1"

        """
        logger.debug(f"Processing command: {inbound_command}")

        # need to split args and command? aka get first item in inbound_Cmmand,
        # then the rest are args? - let the command itself do that

        split_command = inbound_command.split()
        command = split_command[0]
        args_list = split_command[1:]

        # have the factory choose WHCIH command class to create based on inputted command
        # create it, and return it to use
        command_instance = self.command_factory.create_command(
            command_name=command, args_list=args_list, agent_id=self.agent_id
        )

        # run the command instance, which will queue up the needed commands based
        # on inputs, etc. and so forth. Entirely up to the user to do
        command_instance.run()

    def _check_if_command_is_in_script(self, inbound_command):
        """
        Checks if the given command exists in the script.
        Safeguards against empty or malformed scripts.
        """

        """
        if inbound_command not in self.generated_commands:
            return False

        
        
        
        """

    def extract_help_info(self):
        """
        Extracts help info from the script contents and returns it as a single string.

        Used for easy parsing of the yaml for a help dialogue. Mainly used by a custom "help"
        handler for when running the "help" command
        """
        try:
            help_info = []
            help_info.append(f"> Extension Script `{self.script_name}` options:\n")
            for command in self.script_contents["commands"]:
                name = command.get("name", "Unknown Command")
                desc = command.get("description", "No description provided")
                help_info.append(f"\t{name}: {desc}\n")

            # Join all lines into a single string
            return "".join(help_info)
        except Exception as e:
            logger.error(e)
            return "Error creating help dialogue from script"


# Example usage:
if __name__ == "__main__":
    factory = CommandFactory()
    # Load the module that contains one or more command classes
    factory.load_command_module(
        "ping_host.py"
    )  # The file should define at least one class that extends BaseCommand

    # Create a command instance by its registered name
    try:
        cmd = factory.create_command("ping_host", ["127.0.0.1"])
        cmd.run()
    except Exception as e:
        print(f"Error: {e}")
