import json
import signal
import socket
import struct
from multiprocessing import Process

from flask import request
from modules.client import BaseAgent
from modules.instances import Instance
from modules.listener import BaseListener
from modules.log import log

# from modules.redis_models import ActiveService
from modules.utils import api_response, generate_timestamp, generate_unique_id
from plugins.file_beacon_v1.modules.listener import Listener
from plugins.file_beacon_v1.modules.vlmt import VLMT

app = Instance().app
logger = log(__name__)


class Info:
    name = "file-beacon-v1"
    author = "ryanq.47"


"""
Plan: 
 - Class:
     - Maybe the socket stuff?
     - Would also need a client class, that handles furtehr processing. replace handle_client.

    On cilent class load, inheret the Client base class, and it will load data from redis if client exists



"""


# problem - getting defined multiple times/called multiple times
# Using flask, create endpoint for enqueuing command
# print("ROUTING")
@app.route(
    "/plugin/file-beacon-v1/agent/<string:agent_uuid>/command", methods=["GET", "POST"]
)
def flask_enqueue_agent_command(agent_uuid):
    data = request.get_json()
    # use BaseAgent to properly enqueue here
    # take in command as json?
    command = data.get("command")

    return api_response(data=f"The UUID is: {agent_uuid}")


@app.route("/plugin/file-beacon-v1/listener/spawn", methods=["POST"])
def flask_spawn_listener():
    data = request.get_json()
    # get data as json
    # spawn listener w it
    listener_port = data.get("port")
    listener_host = data.get("host")

    new_listener = Listener(port=listener_port, host=listener_host)
    new_listener.spawn()

    return api_response(data="somedata")


@app.route(
    "/plugin/file-beacon-v1/listener/<string:listener_uuid>/kill", methods=["POST"]
)
def flask_kill_listener():
    ...  # Kill listener. add a kill func to listener
    # data = request.get_json()
    # # get data as json
    # # spawn listener w it
    # listener_port = data.get("port")
    # listener_host = data.get("host")

    # new_listener = Listener(port=listener_port, host=listener_host)
    # new_listener.spawn()

    # return api_response(data="somedata")
