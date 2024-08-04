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

# Configuration Setup
logger.debug("Setting up config singleton")
launch_path = pathlib.Path(__file__).parent
config_file = launch_path / "config" / "config.yaml"

# Config Singleton
config = Config()
config.launch_path = launch_path  # Adding custom launch_path attribute
config.load_config(config_file=config_file)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///users.db"  # puts in instance/users.db
)
app.config["SECRET_KEY"] = config.config.server.authentication.secret_key
app.config["JWT_SECRET_KEY"] = config.config.server.authentication.secret_key
app.config["JWT_TOKEN_LOCATION"] = ["headers"]

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
