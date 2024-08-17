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
from modules.utils import plugin_loader, generate_unique_id
from modules.config import Config
from modules.instances import Instance
import pathlib
import time
import bcrypt

logger = log(__name__)

# Configuration Setup - GOES FIRST
logger.debug("Setting up config singleton")
launch_path = pathlib.Path(__file__).parent
config_file = launch_path / "config" / "config.yaml"
env_file = launch_path / ".env"

# make sure instance path is ALWAYS under the app folder
instance_path = launch_path / "instance"

# Setup app variable, second.
# Gunicorn want's the app to be globally accessible.
app = Flask(__name__, instance_path=instance_path)

# the rest of the crap
# Config Singleton
Config().launch_path = launch_path  # Adding custom launch_path attribute
Config().load_config(config_file=config_file)
Config().load_env(env_file=env_file)

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

# Plugin Loader
plugin_loader()


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


# Used when calling whispernet.py directly
if __name__ == "__main__":
    try:
        app.run(debug=True, port=8081)

    except Exception as e:
        print(e)
