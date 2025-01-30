import json
import signal
import socket
import struct
from multiprocessing import Process

from flask import request
from flask_jwt_extended import jwt_required  # if you need JWT
from flask_restx import Namespace, Resource, fields

from modules.agent import BaseAgent
from modules.instances import Instance
from modules.listener import BaseListener
from modules.log import log

from plugins.beacon_http.modules.listener import Listener

# from modules.redis_models import ActiveService
from modules.utils import api_response, generate_timestamp, generate_unique_id


logger = log(__name__)

app = Instance().app

"""
Meant for managing listeners + their clients

"""


class Info:
    name = "beacon_http"
    author = "ryanq.47"


# ------------------------------------------------------------------------------------
#   1) Create a dedicated Namespace for the Beacon HTTP plugin
# ------------------------------------------------------------------------------------
beacon_http_ns = Namespace(
    "Plugin: beacon-http",
    description="Beacon HTTP plugin endpoints",
)

# ------------------------------------------------------------------------------------
#   2) Define a standard response model (similar to stats_response in your example)
# ------------------------------------------------------------------------------------
beacon_http_response = beacon_http_ns.model(
    "BeaconHttpResponse",
    {
        "rid": fields.String(description="Request ID"),
        "timestamp": fields.String(description="Request Timestamp, Unix Time"),
        "status": fields.Integer(description="Response Code", default=200),
        "data": fields.Raw(description="Data from server response"),
        "message": fields.String(description="Message or status info"),
    },
)

# ------------------------------------------------------------------------------------
#   3) Define Resource classes + routes
# ------------------------------------------------------------------------------------


@beacon_http_ns.route("/agent/<string:agent_uuid>/command")
class BeaconHttpAgentCommandResource(Resource):
    """
    POST /plugin/beacon-http/agent/<string:agent_uuid>/command
    """

    @beacon_http_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            500: "Server Error",
        },
        description="Enqueue a command for the specified agent.",
    )
    @beacon_http_ns.expect(  # optional: define an input model if desired
        beacon_http_ns.model(
            "AgentCommandInput",
            {
                "command": fields.String(
                    required=True, description="Command to enqueue"
                ),
            },
        )
    )
    @beacon_http_ns.marshal_with(beacon_http_response, code=200)
    # @jwt_required  # If your API is protected by JWT
    def post(self, agent_uuid):
        """
        POST a command to a specific agent.
        For example: {"command": "whoami"}
        """
        data = request.get_json() or {}
        command = data.get("command")

        # Use your BaseAgent logic to enqueue the command
        # e.g., BaseAgent.enqueue_command(agent_uuid, command)

        return api_response(data=f"Received command '{command}' for agent {agent_uuid}")


@beacon_http_ns.route("/listener/spawn")
class BeaconHttpListenerSpawnResource(Resource):
    """
    POST /plugin/beacon-http/listener/spawn
    """

    @beacon_http_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            500: "Server Error",
        },
        description="Spawn a new listener with the specified host and port.",
    )
    @beacon_http_ns.expect(
        beacon_http_ns.model(
            "SpawnListenerInput",
            {
                "port": fields.Integer(
                    required=True, description="Port for the new listener"
                ),
                "host": fields.String(
                    required=True, description="Host/IP for the new listener"
                ),
            },
        )
    )
    @beacon_http_ns.marshal_with(beacon_http_response, code=200)
    # @jwt_required
    def post(self):
        """
        POST a request to spawn a new listener process.
        Example JSON: {"port": 8080, "host": "0.0.0.0"}
        """
        data = request.get_json() or {}
        listener_port = data.get("port")
        listener_host = data.get("host")

        # Instantiate your custom Listener class (from your plugin)
        new_listener = Listener()
        new_listener.spawn(port=listener_port, host=listener_host)

        return api_response(data=f"Spawned listener on {listener_host}:{listener_port}")


@beacon_http_ns.route("/listener/<string:listener_uuid>/kill")
class BeaconHttpListenerKillResource(Resource):
    """
    POST /plugin/beacon-http/listener/<string:listener_uuid>/kill
    """

    @beacon_http_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            500: "Server Error",
        },
        description="Kill a running listener by UUID.",
    )
    @beacon_http_ns.marshal_with(beacon_http_response, code=200)
    # @jwt_required
    def post(self, listener_uuid):
        """
        POST to kill the specified listener.
        """
        # Example logic:
        # listener = Listener.get(listener_uuid)
        # if not listener:
        #     return api_response(status=404, data="Listener not found.")
        # listener.kill()

        #

        # gonna have to figure thi sout
        # TypeError: Listener.__init__() missing 2 required positional arguments: 'port' and 'host'
        # 127.0.0.1 - - [30/Jan/2025 18:10:07] "POST /plugin/beacon-http/listener/58416112-99bc-45eb-9b1e-88d179c0b7aa/kill HTTP/1.1" 500 -

        listener = Listener(listener_id=listener_uuid)
        listener.kill()

        return api_response(data=f"Listener {listener_uuid} killed (placeholder).")


# ------------------------------------------------------------------------------------
#   4) Register the namespace with your Flask-RESTX Api
#      This is typically done once in your initialization code.
# ------------------------------------------------------------------------------------
Instance().api.add_namespace(beacon_http_ns, path="/plugin/beacon-http")
