from flask import jsonify, request, send_from_directory
from modules.binary_models import Agent, Custom, Dropper
from modules.config import Config
from modules.instances import Instance
from modules.log import log
from modules.utils import api_response

logger = log(__name__)
app = Instance().app


class Info:
    name = "binary_builder"
    author = "ryanq.47"


# Optional route example
@app.route("/binary_builder", methods=["GET"])
def buinary_builder():
    return jsonify({"somekey": "somevalue"})


## routes:
# /binary_builder/<name_of_target?>

# then if tree it for names based on supported items?
# not super modular but it works

# dep
"""
@app.route('/binary_builder/<target>', methods=['POST'])
def build_target(target):
    try:
        match target:
            case "x64_windows_dropper":
                logger.info("Building target: x64_windows")
                # get config value
                dockerfile_path = Config().config.server.binaries.dropers.x64_windows_dropper
            case _:
                logger.info(f"Unknown target: {target}")
                return api_response(
                    message="Unknown target",
                    code=400
                )

        output_dir      = str((Config().launch_path / "data" / "compiled").absolute())
        build_context   = str(Config().root_project_path) #str((Config().launch_path).absolute() / "..")

        logger.debug(f"Compiled output directory: {output_dir}")
        logger.debug(f"Docker build Context: {build_context}")

        #output_dir = "./data/compiled/" #pathify this

        build(
            dockerfile_path = dockerfile_path,
            output_dir = output_dir,
            build_context = build_context
        )

        return api_response(
            message=f"successfully built {target}",
            status=200
        )

    except Exception as e:
        logger.error(e)
        return api_response(
            message="An error occured",
            status=500
        )       
"""


@app.route("/binary-builder/build/custom", methods=["POST"])
def build_custom():
    """
    Build target

    json:

    {
        "target":"x64_windows_dropper,
        "shellcode":"aabbcc=="
        "binary_name":"somename"
    }

    """
    try:
        dict_data = request.get_json()
        required_keys = ["target", "shellcode", "binary_name"]
        missing_keys = [
            key for key in required_keys if not dict_data or dict_data.get(key) is None
        ]

        logger.debug(dict_data)

        if missing_keys:
            logger.debug("Missing keys")
            return api_response(message=f"Missing fields in request", status=400)

        # Extract values since all are validated
        target = dict_data["target"]
        payload = dict_data["shellcode"]
        binary_name = dict_data["binary_name"]

        c = Custom(build_target=target, binary_name=binary_name, payload=payload)

        c.build()

        return api_response(message=f"successfully built {target}", status=200)

    except Exception as e:
        logger.error(e)
        return api_response(message="An error occured", status=500)


# [ ] not done
@app.route("/binary-builder/build/dropper", methods=["POST"])
def build_dropper():
    """
    Build target

    json:

    {
        "target":"x64_windows_dropper,
    }

    """
    try:
        dict_data = request.get_json()
        required_keys = ["target", "ip", "port", "binary_name"]
        missing_keys = [
            key for key in required_keys if not dict_data or dict_data.get(key) is None
        ]

        if missing_keys:
            return api_response(message=f"Missing fields in request", status=400)

        # Extract values since all are validated
        target = dict_data["target"]
        ip = dict_data["ip"]
        port = dict_data["port"]
        binary_name = dict_data["binary_name"]

        d = Dropper(
            build_target=target,
            server_address=ip,
            server_port=port,
            binary_name=binary_name,
        )

        return api_response(message=f"successfully built {target}", status=200)

    except Exception as e:
        logger.error(e)
        return api_response(message="An error occured", status=500)


# [ ] not done
@app.route("/binary-builder/build/agent", methods=["POST"])
def build_agent():
    """
    Build agent
    """
    try:
        dict_data = request.get_json()
        required_keys = ["target", "ip", "port", "binary_name"]
        missing_keys = [
            key for key in required_keys if not dict_data or dict_data.get(key) is None
        ]

        if missing_keys:
            return api_response(message=f"Missing fields in request", status=400)

        # Extract values since all are validated
        target = dict_data["target"]
        ip = dict_data["ip"]
        port = dict_data["port"]
        binary_name = dict_data["binary_name"]

        a = Agent(
            build_target=target,
            server_address=ip,
            server_port=port,
            binary_name=binary_name,
        )

        a.build()

        return api_response(message=f"successfully built {target}", status=200)

    except Exception as e:
        logger.error(e)
        return api_response(message="An error occured", status=500)


# serve the binaires
@app.route("/binary-builder/binaries/<path:filename>", methods=["GET"])
def compiled_binaries(filename):
    """
    Serve the compiled binaries from the /data/compiled directory
    """
    try:
        # DON"T use resolve/absolute, might result in dir traversal
        bin_path = Config().root_project_path / "data" / "compiled"

        # Use send_from_directory to serve the file
        return send_from_directory(bin_path, filename)
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return api_response(status=404, message="File not found")

    except Exception as e:
        logger.error(e)
        return api_response(status=500)


# GEt list of binaries
@app.route("/binary-builder/binaries", methods=["GET"])
def list_binaries():
    """
    Get a list of all the binaries in the folder, and the path they are at
    """
    bin_path = Config().root_project_path / "data" / "compiled"

    # Initialize a dictionary to hold filenames and their paths
    binaries = {}

    # Walk through the directory and add each file to the dictionary
    for file_path in bin_path.iterdir():
        if file_path.is_file():
            # Add the filename and its endpoint path to the dictionary
            binaries[file_path.name] = f"binary-builder/binaries/{file_path.name}"

    # Return the dictionary as a JSON response
    return api_response(data=binaries)


@app.route("/binary-builder/targets", methods=["GET"])
def valid_targets():
    """
    Returns a list of valid compile targets
    """
    try:

        droppers_dict = {
            key: (value if value else "No buildfile")
            for key, value in Config().config.server.binaries.droppers.items()
        }

        agents_dict = {
            key: (value if value else "No buildfile")
            for key, value in Config().config.server.binaries.agents.items()
        }

        customs_dict = {
            key: (value if value else "No buildfile")
            for key, value in Config().config.server.binaries.customs.items()
        }

        final_response = {
            "droppers": droppers_dict,
            "agents": agents_dict,
            "customs": customs_dict,
        }

        """ Output example: 
            {
            "data": {
                "agents": {
                "x64_windows": "No Dockerfile"
                },
                "droppers": {
                "x64_windows": "_docker/dockerfiles/debian_windows_x64.dockerfile",
                "x86_windows": "No Dockerfile"
                }
            },
            "message": "",
            "rid": "af073584-5af9-4592-9338-0ebc03e49310",
            "status": 200,
            "timestamp": 1728241553
            }
        """

        return api_response(data=final_response)

    except Exception as e:
        logger.error(e)
        return api_response(status=500)
