import yaml
import munch
import pathlib
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
        if not hasattr(self, "initialized"):
            self.value = None
            self.initialized = True

        # non-config file values (env vars, etc)
        self.example = "somevalue"
        self.launch_path = None

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
