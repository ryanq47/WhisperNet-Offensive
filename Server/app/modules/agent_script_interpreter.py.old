import pathlib
import yaml
from modules.config import Config
from modules.log import log

logger = log(__name__)


class AgentScriptInterpreter:
    def __init__(self, script_name: str):
        """
        Initializes the script interpreter with the given script name.
        Loads and parses the YAML script.
        """
        if not script_name:
            raise ValueError("Cannot have a blank script name.")

        self.script_name = script_name

        # Load script path
        self.root_project_path = pathlib.Path(Config().root_project_path)
        self.script_path = (
            self.root_project_path / "data" / "scripts" / self.script_name
        )

        logger.debug(f"Script Path: {self.script_path}")

        # Load YAML script
        try:
            with open(self.script_path, "r") as file:
                self.script_contents = (
                    yaml.safe_load(file) or {}
                )  # Default to empty dict if None
        except FileNotFoundError:
            logger.error(f"Script file not found: {self.script_path}")
            raise FileNotFoundError(f"Script file not found: {self.script_path}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML script: {e}")
            raise ValueError(f"Error parsing YAML script: {e}")

    def process_command(self, inbound_command):
        """
        Processes the given command from the script.
        If found, returns a list of full command strings to enqueue.
        If not found, logs an error and returns False.
        """
        try:
            # Initialize command queue
            command_queue_list = []

            # Check if the command exists
            if not self._check_if_command_is_in_script(inbound_command):
                logger.warning(f"Command '{inbound_command}' not found in script.")
                return False

            # Locate the matching command
            command = next(
                (
                    cmd
                    for cmd in self.script_contents.get("commands", [])
                    if cmd.get("name") == inbound_command
                ),
                None,
            )

            if not command:
                logger.error(
                    f"Command '{inbound_command}' was expected but not found in script."
                )
                return False

            # Extract command details
            command_name = command.get("name", "Unknown Command")
            command_description = command.get(
                "description", "No description available."
            )
            command_steps = command.get("steps", [])

            if not command_steps:
                logger.warning(f"Command '{command_name}' has no steps defined.")
                return False

            for step in command_steps:
                try:
                    action = step.get("action")
                    args = step.get("args", [])

                    if not action:
                        logger.warning(
                            f"Skipping step with missing action in command '{command_name}'."
                        )
                        continue

                    # Convert list of args into a single space-separated string
                    args_str = (
                        " ".join(map(str, args))
                        if isinstance(args, list)
                        else str(args)
                    )

                    # Combine action and args into a single string
                    full_command = f"{action} {args_str}".strip()

                    # Append the command to the queue list
                    command_queue_list.append(full_command)

                except Exception as e:
                    logger.error(f"Error processing step in '{command_name}': {e}")

            logger.debug(f"Processed command '{command_name}': {command_queue_list}")
            return command_queue_list

        except Exception as e:
            logger.error(f"Unexpected error in process_command: {e}")
            return False

    def _check_if_command_is_in_script(self, inbound_command):
        """
        Checks if the given command exists in the script.
        Safeguards against empty or malformed scripts.
        """
        try:
            return any(
                inbound_command == entry.get("name", "")
                for entry in self.script_contents.get("commands", [])
            )
        except Exception as e:
            logger.error(f"Error checking command in script: {e}")
            return False

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


# Run only if executed directly
if __name__ == "__main__":
    try:
        a = AgentScriptInterpreter("script1.yaml")
        result = a.process_command("recon")
        if result:
            print("Commands to execute:", result)
        else:
            print("Command not found or failed to process.")
    except Exception as e:
        logger.critical(f"Fatal error in script execution: {e}")
