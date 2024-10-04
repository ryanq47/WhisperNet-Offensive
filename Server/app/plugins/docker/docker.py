from flask import jsonify
from modules.instances import Instance
from modules.log import log
from modules.utils import api_response
from modules.docker_handler import stop_container, start_container
import re

logger = log(__name__)
app = Instance().app

class Info:
    name = "docker"
    author = "ryanq.47"

# Optional route example
@app.route('/docker', methods=['GET'])
def plugin_route():
    return jsonify({"somekey": "somevalue"})

@app.route('/docker/start/<container_name>', methods=['POST'])
def docker_start(container_name):
    try:
        if not validate_container_name(container_name):
            return api_response(message="Invalid container name", status=400)

        ## run the stop w lib

        start_container(container_name)

        ## return 200
        return api_response(message="Container started", status=200)

    except Exception as e:
        logger.error(e)
        return api_response(message="Error starting container", status=500)

@app.route('/docker/stop/<container_name>', methods=['POST'])
def docker_stop(container_name):

    try:
        if not validate_container_name(container_name):
            return api_response(message="Invalid container name", status=400)

        ## run the stop w lib

        stop_container(container_name)

        ## return 200
        return api_response(message="Container stopped", status=200)

    except Exception as e:
        logger.error(e)
        return api_response(message="Error stopping container", status=500)


# sanity check to validate docker container names. 
def validate_container_name(name):
    # Use a regex to allow only alphanumeric characters, dashes, and underscores
    if re.fullmatch(r'[a-zA-Z0-9_-]+', name):
        return True
    return False