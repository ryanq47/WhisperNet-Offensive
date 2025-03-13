import pathlib
import time

import bcrypt
from flask import Flask, jsonify, redirect, request, session, url_for
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from modules.banner import print_banner
from modules.config import Config

from modules.instances import Instance
from modules.log import log
from modules.utils import generate_unique_id, plugin_loader
from modules.startup import start_containers, respawn_listeners, enable_redis_backups

print_banner()

logger = log(__name__)


########################################
# Singleton Config
########################################

# Configuration Setup - GOES FIRST
logger.debug("Setting up config singleton")
launch_path = pathlib.Path(__file__).parent
config_file = launch_path / "config" / "config.yaml"
env_file = launch_path / ".env"

# make sure instance path is ALWAYS under the app folder
instance_path = launch_path / "instance"

# Setup app variable, second.
# Gunicorn wants the app to be globally accessible.
app = Flask(__name__, instance_path=instance_path)
api = Api(app)

# the rest of the crap
# DOC THESE
# Config Singleton
Config().launch_path = launch_path  # Adding custom launch_path attribute
# project path is the root path of project
Config().root_project_path = Config().launch_path / "../"

if not config_file.exists():
    exit("config.yaml file does not exist, cannot continue.")
Config().load_config(config_file=config_file)

if not env_file.exists():
    exit(
        ".env file does not exist, please copy example.env into .env & fill out appropriately"
    )

Config().load_env(env_file=env_file)

########################################
# App Config
########################################
# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///users.db"  # puts in instance/users.db
)
app.config["SECRET_KEY"] = Config().env.secret_key
app.config["JWT_SECRET_KEY"] = Config().env.jwt_secret_key
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = (
    Config().config.server.authentication.jwt.expiration
)
app.config["PROPAGATE_EXCEPTIONS"] = (
    True  # allows try/except + proper errors to fall throguh, and allow accurate response codes, not just 500 everything
)

########################################
# Instance Setup
########################################
# Instance Setup
logger.debug("Setting up instances")

# JWT Manager Instance
Instance().jwt_manager = JWTManager(app)

# Database Instance
db = SQLAlchemy(app)
Instance().db_engine = db
# Import models after the singleton setup
from modules.models import *

# Create database tables within the app context
with app.app_context():
    db.create_all()

# Application Instance
Instance().app = app
Instance().api = api

########################################
# Additional Startup Tasks
########################################

## Everything that relies on Instance stuff, goes AFTER this line
logger.debug("Loading containers...")
start_containers()
enable_redis_backups()

# Plugin Loader
logger.info("Loading Plugins...")
plugin_loader()

logger.info("Restarting listeners...")
respawn_listeners()

# add default user if DB is empty
# kinda fugly but it works
with app.app_context():
    # Query to check if any users exist
    user_count = User.query.count()

    if user_count == 0:
        logger.warning("No users found, creating default user with creds from .env")
        logger.debug("Hashing password for default user...")
        hashed_password = bcrypt.hashpw(
            Config().env.default_password.encode(),
            bcrypt.gensalt(rounds=Config().config.server.authentication.bcrypt.rounds),
        )
        default_user = User(
            username=Config().env.default_username,
            password=hashed_password,
            uuid=generate_unique_id(),
        )
        # Add and commit the new user to the database
        db.session.add(default_user)
        db.session.commit()
        logger.info(f"Created default user: {Config().env.default_username}")
    else:
        logger.info("User DB is not empty, not adding default user.")


# Used when calling from Gunicorn
def start():
    try:
        app.run(debug=False)
    except Exception as e:
        print(e)


# Used when calling HCKD.py directly
if __name__ == "__main__":
    try:
        ## CANNOT have debug mode on for multiple instances/http listeners. yay
        # app.run(debug=False, port=8081, host="0.0.0.0", threaded=True)

        from waitress import serve

        serve(app=app, port=8081, host="0.0.0.0")

    except Exception as e:
        print(e)
