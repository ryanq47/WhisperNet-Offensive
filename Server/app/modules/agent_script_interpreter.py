## Script interpreter for agent scripts
import pathlib
import yaml
from modules.config import Config


class AgentScriptInterpreter:
    def __init__(self, script_name: str):
        if script_name == None:
            raise Exception(f"Cannot have blank script name: '{script_name}'")

        self.script_name = script_name

        # load YAML
        self.root_project_path = pathlib.Path(Config().root_project_path)

        print(self.root_project_path)

        self.script_path = (
            self.root_project_path
            / "data"
            / "scripts"
            / "script1.yaml"  # self.script_name - coming in as blank
        )

        print(self.script_path)

        with open(self.script_path, "r") as file:
            self.script_contents = yaml.safe_load(file)

    def process_command(self, inbound_command):
        """
        Takes in agent command, compares against script

        If in script, enqueues commands (or returns a list of dict commands to enqueue <<) for the agent.

        If not in script, returns false

        """
        # Initialize an empty command queue
        command_queue_list = []

        # Check if the command exists in the script
        if not self._check_if_command_is_in_script(inbound_command):
            print(f"Command '{inbound_command}' not found in script.")
            return False

        # Locate the matching command by filtering through the list of commands
        # use this as new dict base
        command = None
        for cmd in self.script_contents.get("commands", []):
            if cmd.get("name") == inbound_command:
                command = cmd
                break  # Exit loop once found

        # If no matching command is found, return False
        # This shouldn't happen due to the check above
        if not command:
            print(f"Command '{inbound_command}' not found in script.")
            return False

        # Extract relevant command details
        command_name = command.get("name")
        command_description = command.get("description", "No description available.")
        command_steps = command.get("steps", [])

        # If no steps are defined, return False
        if not command_steps:
            print(f"Command '{command_name}' has no steps defined.")
            return False

        for step in command_steps:
            # might hit issues here with multiple ", or '
            action = step.get("action")
            args = step.get("args", [])

            # Convert list of args into a single space-separated string
            args_str = " ".join(args) if isinstance(args, list) else str(args)

            # Combine action and args into a single string
            full_command = f"{action} {args_str}".strip()

            # Append to the command queue list, in full command, ex: "shell whoami /all"
            command_queue_list.append(full_command)

        # # Print formatted command details for debugging
        # print(f"Processed Command: {command_name} - {command_description}")
        # for cmd in command_queue_list:
        #     print(f"  -> Command: {full_command}")

        print(command_queue_list)

        return command_queue_list  # Returning the list of command dictionaries

    def _check_if_command_is_in_script(self, inbound_command):
        """
        Checks if a commadn is in the script, if not, returns false.

        Safeguards a bit too for if the script is empty, etc.

        """
        try:
            # make sure the command actually exists in the script, else pass on
            for entry in self.script_contents.get("commands", []):
                if inbound_command == entry.get("name", ""):
                    return True

        except Exception as e:
            return False

        return False


if __name__ == "__main__":
    a = AgentScriptInterpreter(
        "/home/kali/Documents/GitHub/WhisperNet-Offensive/Server/data/scripts/script1.yaml"
    )
    a.process_command("recon")
