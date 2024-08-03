from flask import Flask, jsonify, session, request, redirect, url_for
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from flask_sqlalchemy import SQLAlchemy
from modules.log import log
from modules.utils import plugin_loader
from modules.config import Config
from modules.instances import Instance
import pathlib
import time


logger = log(__name__)
# Gunicorn want's the app to be globally accessible.
app = Flask(__name__)

logger.debug("Setting up config singleton")  # setup config
# Absolute path to this file being run, handy for running from any dir
launch_path = pathlib.Path(__file__).parent
config_file = launch_path / "config" / "config.yaml"
Config().launch_path = (
    launch_path  # Note, this does not exist by default in the config class
)
Config().load_config(config_file=config_file)

# User Setup
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///databases/users.db"
app.config["SECRET_KEY"] = Config().config.server.authentication.secret_key
app.config["JWT_SECRET_KEY"] = Config().config.server.authentication.secret_key
app.config["JWT_TOKEN_LOCATION"] = ["headers"]


# setting up instances
logger.debug("Setting up instances")
Instance().jwt_manager = JWTManager(app)  # jwt manager
# db engine - might have some issues here w concurrency, not sure how this will be used yet.
Instance().db_engine = SQLAlchemy(app)
Instance().app = app
plugin_loader()


# Used when calling from Gunicorn
def start():
    try:
        app.run(debug=False)
    except Exception as e:
        print(e)


# Used when calling whispernet.py directly
if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        print(e)
