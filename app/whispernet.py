from flask import Flask
from modules.log import log
from modules.config import Config
import pathlib

logger = log(__name__)

logger.debug("Setting up config singleton")  # setup config
# Absolute path to this file being run, handy for running from any dir
launch_path = pathlib.Path(__file__).parent
config_file = launch_path / "config" / "config.yaml"
Config().launch_path = launch_path
Config().load_config(config_file=config_file)


if __name__ == "__main__":
    try:
        whispernet = Flask(__name__)
        whispernet.run(debug=True)
    except Exception as e:
        print(e)
