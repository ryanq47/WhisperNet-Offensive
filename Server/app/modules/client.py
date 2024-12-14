import json
import pathlib

import munch
import yaml


class Client:
    """
    A base class that provides common functionality for all models.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        # may or may not be needed
        self.alias = None
        self.template = None

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
                print("Missing 'template' section in configuration.")
                raise ValueError("Configuration must include a 'template' section.")

            if alias_dict is None:
                print("Missing 'alias' section in configuration.")
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
            print(f"Configuration file not found: {config_file_path}")
            print(fnfe)
            raise fnfe

        except Exception as e:
            print(e)
            raise e

    def _load_alias(self, alias_dict: dict):
        """
        Internal
        Loads alias into client.

        Seperate method for future handling/standard way of handling
        """
        try:
            # munchify the dicts for better/easier access
            self.alias = munch.munchify(alias_dict)

            print("alias:")
            # .keys: keys
            # .values: values
            # .items: key, value pair
            for key, val in self.alias.items():
                print(f"\t{key}: {val}")

        except Exception as e:
            print(e)
            raise e

    def _load_template(self, template_dict: dict):
        """
        Internal
        Loads alias into client.

        Seperate method for future handling/standard way of handling

        """
        try:
            # munchify the dicts for better/easier access
            self.template = munch.munchify(template_dict)

            print("template:")
            # .keys: keys
            # .values: values
            # .items: key, value pair
            for key, val in self.template.items():
                print(f"\t{key}: {val}")

        except Exception as e:
            print(e)
            raise e

    def format_command(self, command: str, arguments: str):
        """
        Auto format a template string

        command (str): The command. Used for lookups in config.yaml

        arguments (str): The arguments

        Ex:

        powershell iex bypass; powershell %%COMMAND%%
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
                print(f"Command template for '{command}' not found")
                return

            # Replace %%COMMAND%% with the provided arguments
            formatted_command = command_template.replace("%%COMMAND%%", arguments)
            print(formatted_command)

            return formatted_command

        except Exception as e:
            print(e)
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
                print("Missing 'template' section in configuration.")
                return False
                # raise ValueError("Configuration must include a 'template' section.")

            if alias_dict is None:
                # err
                print("Missing 'alias' section in configuration.")
                return False
                # raise ValueError("Configuration must include an 'alias' section.")

            if info_dict is None:
                # warning
                print("Missing 'info' section in configuration - warning, not error")

            return True

        except FileNotFoundError as fnfe:
            print(f"Configuration file not found: {config_file_path}")
            print(fnfe)
            raise fnfe

        except Exception as e:
            print("An error not related to the config file contents occured:")
            print(e)
            raise e


# ## Basic example of usage
# client = Client()
# ## load config - NEEDS to be called first
# client.load_config(config_file_path="example.yaml")

# ## make sure to run this every time before command gets sent off
# ## LOG the before & after as well, in action log or something
# client.format_command(command="powershell", arguments="whoami")

# print(client.validate_config(config_file_path="example.yaml"))

"""
Then like

comamnd comes in,         gets intercepted by model, parsed, and adjusted dynamically as needed based on config?
exec:powershell whoami ->  ...                               exec:powershell -c -noUAC "whoami"

makes it easier for the user, however a tad bit less transparent on what's happening under the hood

Shortcomings: still need to find out how to call this, other than popen or something.
"""
