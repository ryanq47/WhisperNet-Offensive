"""
Prefork considerations
   - The Instance singleton is used to hold references to application-wide components like JWTManager and SQLAlchemy.
   - Each worker process creates its own instance of these components, which are used independently within each process.
   - Since Flask workers do not share memory, this design avoids issues with shared mutable state.
"""

import flask
from flask_sqlalchemy import SQLAlchemy
from modules.log import log
from typing import Optional

logger = log(__name__)


class Instance:
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

        # Initialize any other instances here
        self._app = None
        self._db_engine = None

    @property
    def app(self):
        if self._app is None:
            raise ValueError("The app instance has not been set yet.")
        return self._app

    @app.setter
    def app(self, value):
        if isinstance(value, flask.Flask):
            self._app = value
        else:
            raise TypeError(
                f"Expected an instance of 'flask.Flask', but got '{type(value).__name__}' instead."
            )

    @property
    def db_engine(self):
        if self._db_engine is None:
            raise ValueError("The db_engine instance has not been set yet.")
        return self._db_engine

    @db_engine.setter
    def db_engine(self, value):
        if isinstance(value, SQLAlchemy):
            self._db_engine = value
        else:
            raise TypeError(
                f"Expected an instance of 'SQLAlchemy', but got '{type(value).__name__}' instead."
            )
