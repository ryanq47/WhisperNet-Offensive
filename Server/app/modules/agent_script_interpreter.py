## Script interpreter for agent scripts
import pathlib
import yaml


class AgentScriptInterpreter:
    def __init__(self, script_path: str | pathlib.Path):
        self.script_path = script_path

        # load YAML

        with open(self.script_path, "r") as file:
            self.script_contents = yaml.safe_load(file)

    def process_command(self):
        """
        Takes in agent command, compares against script

        If in script, enqueues commands (or returns a list of dict commands to enqueue <<) for the agent.

        If not in script, returns false

        """
        # Iterate through each command entry
        for entry in self.script_contents.get("commands", []):
            name = entry.get("name")
            description = entry.get("description")
            steps = entry.get("steps", [])

            print(f"Command: {name}")
            print(f"  Description: {description}")

            for step in steps:
                action = step.get("action")
                args = step.get("args", [])
                print(f"  - Action: {action}, Args: {args}")


if __name__ == "__main__":
    a = AgentScriptInterpreter(
        "/home/kali/Documents/GitHub/WhisperNet-Offensive/Server/data/scripts/script1.yaml"
    )
    a.process_command()
