"""
This module handles the configuration management for the application.
It uses a singleton pattern to ensure only one instance of the configuration is loaded, which also  eases access to config values,
rather than passing a config object throughout everything.

Classes:
    - Config: Manages loading and accessing the configuration.

Functions:
    - load_config: Loads the configuration from a specified YAML file.

Usage:
    # First call

        # load config file pathlib object
        config_file = pathlib.Path.cwd() / "app" / "config" / "config.yaml"
        # init Config singleton
        config_obj = Config()
        # load config file
        config_obj.load_config(config_file=config_file)

        # access values
        print(config_obj.example)
        # yaml key
        print(config_obj.config.server.name)
        # OR, because it's a singleton
        print(Config().config.server.name)  # << preffered

    # All other calls
        import config

        # access config values
        Config().config.server.name

        
Pre-Fork Considerations
   - The Config singleton is used to load and store configuration data.
   - It is initialized at startup and remains read-only during the application's runtime. 
   - Since each worker process reads the same configuration file at startup, this ensures consistent configuration across workers.

"""

import yaml
import munch
import pathlib
from dotenv import load_dotenv
import os
from modules.log import log

logger = log(__name__)


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # def load_config(config_file: str | pathlib.Path):
    def __init__(self):
        # Check if already initialized
        if hasattr(self, "initialized") and self.initialized:
            return  # Skip re-initialization

        print("Initializing Instance")

        self.value = None
        self.initialized = True

        # Initialize any other values here

    def load_config(self, config_file: str | pathlib.Path):
        """
        Load config

        Only call me when you want to load/reload the config from file

        config_file: path to config file, absolute, or relative.  str or pathlib obj
        """
        if type(config_file) == pathlib.Path:
            # if a pathlib is passed in, convert path to str
            config_file = str(config_file)

        logger.info(f"Loading config '{config_file}'")
        # yaml loader
        with open(config_file, "r") as f:
            self.config = munch.munchify(yaml.safe_load(f))

    def load_env(self, env_file: str | pathlib.Path):
        """
        Load environment variables from a .env file.

        env_file: path to .env file, absolute, or relative.  str or pathlib obj
        """
        if type(env_file) == pathlib.Path:
            # if a pathlib is passed in, convert path to str
            env_file = str(env_file)

        logger.info(f"Loading environment variables from '{env_file}'")
        load_dotenv(env_file)

        # Create a dictionary of environment variables
        env_vars = {
            "jwt_secret_key": os.getenv("JWT_SECRET_KEY"),
            "secret_key": os.getenv("SECRET_KEY"),
            "default_username": os.getenv("DEFAULT_USERNAME"),
            "default_password": os.getenv("DEFAULT_PASSWORD"),
        }

        # Store the environment variables in a munch object
        self.env = munch.munchify(env_vars)
        logger.info("Environment variables loaded")


if __name__ == "__main__":
    # ONLY works from in here, as root path in not in app dir
    config_file = pathlib.Path.cwd() / "app" / "config" / "config.yaml"
    config_obj = Config()
    config_obj.load_config(config_file=config_file)

    print(config_obj.example)
    # yaml key
    print(config_obj.config.server.name)
    # OR, because it's a singleton
    print(Config().config.server.name)  # << preffered
