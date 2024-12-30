# NOTE! This is not the final resting place for functinos. These should all eventually end up in better described files/locations

import importlib
import random
import sys
import time
import uuid

import flask
from flask import jsonify
from modules.config import Config
from modules.instances import Instance
from modules.log import log
from sqlalchemy.orm.exc import NoResultFound

logger = log(__name__)


# Add warnings N stuff to this
def plugin_loader():
    # Plugin Root Dir
    plugin_dir = Config().launch_path / "plugins"

    # Iterate through all subdirectories in the plugin_dir
    for subdir in plugin_dir.iterdir():
        if subdir.is_dir():
            # Look for the Python file with the same name as the subdirectory
            plugin_path = subdir / f"{subdir.name}.py"

            if plugin_path.is_file():
                plugin_name = subdir.name
                logger.info(f"Plugin '{plugin_name}' discovered")

                try:
                    # Load the module from the file path
                    spec = importlib.util.spec_from_file_location(
                        plugin_name, plugin_path
                    )
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[plugin_name] = module
                    spec.loader.exec_module(module)

                    # Get class name from Info class and execute
                    if hasattr(module, "Info"):
                        Info = getattr(module, "Info")

                    else:
                        logger.warning(
                            f"Plugin '{plugin_name}' skipped: 'Info' class not found."
                        )

                except Exception as e:
                    logger.warning(f"Plugin '{plugin_name}' failed to load: {e}")


def api_response(
    message: str = "",
    data: dict = None,
    data_items: list = None,
    status: int = 200,
    **kwargs,
) -> tuple:
    """
    Helper function to create/construct a response JSON string to send back to the user.

    Args:
        status (str): Status of the response, e.g., "success" or "failure".
        data (dict): Data to be sent back in the response.
        error_message (str): Error message, if any.
        data_items (list): List of tuples (key, value) to add to the data dict.
        status_code (int): status code to send back
        **kwargs: Additional keyword arguments to include in the response.

    Returns:
        tuple: A tuple containing the JSON response and the status code.
    """
    try:
        # Initialize response structure
        response = {
            "rid": generate_unique_id(),  # Unique identifier for this response
            "timestamp": generate_timestamp(),  # Current timestamp
            "status": status,  # not needed, but nice to have
            "data": data if data else {},
            "message": str(message),
        }

        # Add additional data items if provided
        if data_items:
            for key, value in data_items:
                response["data"][key] = value

        # this is a stupid line, not in comlpiance iwth api standard
        # Remove data key if it has no useful content
        # if not response["data"]:
        #    del response["data"]

        # Add any additional keyword arguments, excluding None values
        response.update({k: v for k, v in kwargs.items() if v is not None})

        # Return JSON response with appropriate status code
        return jsonify(response), status
    except Exception as e:
        logger.error(e)
        raise e


def generate_unique_id() -> str:
    """
    Generate a unique message ID using UUIDv4.

    Returns:
        str: A unique UUIDv4 string.
    """
    return str(uuid.uuid4())


@staticmethod
def generate_timestamp() -> int:
    """
    Generate a current timestamp.

    Returns:
        int: The current timestamp in seconds since the epoch.
    """
    return int(time.time())


def generate_mashed_name():
    """
    Generates a mashed name by randomly selecting one adjective and one noun,
    then concatenating them with an underscore.

    Returns:
        str: The mashed name in uppercase, e.g., "MIGHTY_LION"
    """
    # Define two lists of words
    ADJECTIVES = [
        "Swift",
        "Silent",
        "Mighty",
        "Brave",
        "Clever",
        "Fierce",
        "Gentle",
        "Happy",
        "Jolly",
        "Kind",
        "Lucky",
        "Nimble",
        "Quick",
        "Wise",
        "Zealous",
    ]

    NOUNS = [
        "Lion",
        "Tiger",
        "Eagle",
        "Shark",
        "Wolf",
        "Bear",
        "Falcon",
        "Panther",
        "Leopard",
        "Dragon",
        "Phoenix",
        "Hawk",
        "Dolphin",
        "Cobra",
        "Viper",
    ]
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    mashed_name = f"{adjective}_{noun}".upper()
    return mashed_name
