from flask import jsonify, request, send_from_directory
from modules.binary_models import Agent, Custom
from modules.config import Config
from modules.instances import Instance
from modules.log import log
from modules.utils import api_response

logger = log(__name__)
app = Instance().app


class Info:
    name = "binary_builder"
    author = "ryanq.47"


@app.route("/binary-builder/build", methods=["POST"])
def build_binary():
    """
    Build binary based on payload_type.

    JSON request body should include:
    {
        "payload_type": "x86_windows_agent",  # or "x64_windows_custom", etc.
        "ip": "127.0.0.1",                    # Required for agent builds
        "port": "8080",                       # Required for agent builds
        "shellcode": "aabbcc==",              # Required for custom builds
        "binary_name": "somename",
        "delivery_method": "name_of_technique" # Required for custom builds
    }

    Went ahead an combined the endpoints into one for easier API access
    """
    try:
        dict_data = request.get_json()
        logger.debug(f"Request data: {dict_data}")

        if not dict_data:
            return api_response(message="Invalid JSON data", status=400)

        payload_type = dict_data.get("payload_type")
        if not payload_type:
            return api_response(message="Missing 'payload_type' field", status=400)

        # Determine required fields based on payload_type
        if "agent" in payload_type:
            required_keys = ["payload_type", "ip", "port", "binary_name"]
        elif "custom" in payload_type:
            required_keys = [
                "payload_type",
                "shellcode",
                "binary_name",
                "delivery_method",
            ]
        else:
            return api_response(
                message=f"Unknown payload_type '{payload_type}'", status=400
            )

        # Check for missing keys
        missing_keys = [key for key in required_keys if not dict_data.get(key)]
        if missing_keys:
            logger.info(f"Request missing keys: {', '.join(missing_keys)}")
            return api_response(
                message=f"Missing fields: {', '.join(missing_keys)}", status=400
            )

        # Handle the build process
        if "agent" in payload_type:
            # Build agent
            payload_name = dict_data["payload_name"]
            ip = dict_data["ip"]
            port = dict_data["port"]
            binary_name = dict_data["binary_name"]

            agent_builder = Agent(
                payload_name=payload_name,
                server_address=ip,
                server_port=port,
                binary_name=binary_name,
            )
            agent_builder.build()
            return api_response(
                message=f"Successfully built agent '{binary_name}'", status=200
            )

        elif "custom" in payload_type:
            # Build custom
            payload_name = dict_data["payload_name"]
            shellcode = dict_data["shellcode"]
            binary_name = dict_data["binary_name"]
            delivery_name = dict_data["delivery_name"]

            custom_builder = Custom(
                payload_name=payload_name,
                binary_name=binary_name,
                payload=shellcode,
                delivery_name=delivery_name,
            )
            custom_builder.build()
            return api_response(
                message=f"Successfully built custom binary '{binary_name}'", status=200
            )

        else:
            return api_response(message="Invalid 'payload_type'", status=400)

    except Exception as e:
        logger.error(e)
        return api_response(message="An error occurred", status=500)


# Serve the binaries
@app.route("/binary-builder/binaries/<path:filename>", methods=["GET"])
def compiled_binaries(filename):
    """
    Serve the compiled binaries from the /data/compiled directory.
    """
    try:
        bin_path = Config().root_project_path / "data" / "compiled"
        return send_from_directory(bin_path, filename)
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return api_response(status=404, message="File not found")
    except Exception as e:
        logger.error(e)
        return api_response(status=500)


# Get list of binaries
@app.route("/binary-builder/binaries", methods=["GET"])
def list_binaries():
    """
    Get a list of all the binaries in the folder and their paths.
    """
    try:
        bin_path = Config().root_project_path / "data" / "compiled"
        binaries = {}

        for file_path in bin_path.iterdir():
            if file_path.is_file():
                binaries[file_path.name] = f"binary-builder/binaries/{file_path.name}"

        return api_response(data=binaries)
    except Exception as e:
        logger.error(e)
        return api_response(status=500)


@app.route("/binary-builder/targets", methods=["GET"])
def valid_targets():
    """
    Returns a list of valid compile targets.
    """
    try:
        # Extract delivery methods
        delivery_items = Config().config.server.binaries.delivery.items()

        droppers_dict = {
            key: value
            for key, value in delivery_items
            if value.get("type") == "dropper"
        }

        loaders_dict = {
            key: value for key, value in delivery_items if value.get("type") == "loader"
        }

        # Extract payloads
        agents_dict = Config().config.server.binaries.agents
        customs_dict = Config().config.server.binaries.customs

        final_response = {
            "payloads": {
                "agents": agents_dict,
                "customs": customs_dict,
            },
            "delivery": {
                "loaders": loaders_dict,
                "droppers": droppers_dict,
            },
        }

        return api_response(data=final_response)
    except Exception as e:
        logger.error(e)
        return api_response(status=500)
