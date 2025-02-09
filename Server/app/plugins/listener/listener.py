## Plugin for general listener things

import json
import signal
import socket
import struct
from multiprocessing import Process

from flask import request, send_from_directory
from flask_jwt_extended import jwt_required  # if you need JWT
from flask_restx import Namespace, Resource, fields

from modules.agent import BaseAgent
from modules.instances import Instance
from modules.listener import BaseListener
from modules.log import log
import hashlib
from modules.config import Config
import pathlib

# HTTP Imports"
# change these as needed
# from plugins.listener.http.agent import *
# from plugins.listener.http.http_server import *
from plugins.listener.http.listener import Listener

# from modules.redis_models import ActiveService
from modules.utils import api_response, generate_timestamp, generate_unique_id

# ------------------------------------------------------------------------------------
#   Docs
# ------------------------------------------------------------------------------------
"""
# Pre Docs:


"""

logger = log(__name__)
app = Instance().app


class Info:
    name = "listener-manager"
    author = "ryanq.47"


# ------------------------------------------------------------------------------------
#   1) Create a dedicated Namespace for the Beacon HTTP plugin
# ------------------------------------------------------------------------------------
http_ns = Namespace(
    "Plugin: http",
    description="HTTP listener plugin endpoints",
)

listener_manager_ns = Namespace(
    "Plugin: listener-manager",
    description="Manager for listeners",
)


# ------------------------------------------------------------------------------------
#   2) Define a standard response model (similar to stats_response in your example)
# ------------------------------------------------------------------------------------
general_response = http_ns.model(
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


# ------------------------------------------------------------------------------------
#   General
# ------------------------------------------------------------------------------------


@listener_manager_ns.route("/templates")
class ListenerManagerGetTemplatesResource(Resource):
    """
    GET /templates

    get list of agent templates

    """

    # @build_ns.marshal_with(build_response, code=200)
    @jwt_required()
    def get(self):
        # compiled_dir = pathlib.Path(Config().root_project_path) / "data" / "compiled"
        # return send_from_directory(compiled_dir, filename)

        agent_template_dir = (
            pathlib.Path(Config().root_project_path) / "app" / "plugins" / "listener"
        )

        exclude_list = ["__pycache__"]

        # get only directories, which show which agent templates are available
        directories = [
            item.name
            for item in agent_template_dir.iterdir()
            if item.is_dir() and item.name not in exclude_list
        ]

        return api_response(data=directories)


# ------------------------------------------------------------------------------------
#   HTTP
# ------------------------------------------------------------------------------------


@http_ns.route("/spawn")
class HttpListenerSpawnResource(Resource):
    """
    POST /plugin/beacon-http/listener/spawn
    """

    @http_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            500: "Server Error",
        },
        description="Spawn a new listener with the specified host and port.",
    )
    @http_ns.expect(
        http_ns.model(
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
    @http_ns.marshal_with(general_response, code=200)
    @jwt_required()
    def post(self):
        """
        POST a request to spawn a new listener process.
        Example JSON: {"port": 8080, "host": "0.0.0.0"}
        """
        data = request.get_json() or {}
        listener_port = data.get("port")
        listener_host = data.get("host")
        listener_name = data.get("name")

        # Instantiate your custom Listener class (from your plugin)
        new_listener = Listener()
        new_listener.spawn(port=listener_port, host=listener_host, name=listener_name)

        return api_response(data=f"Spawned listener on {listener_host}:{listener_port}")


@http_ns.route("/<string:listener_uuid>/kill")
class HttpListenerKillResource(Resource):
    """
    POST /plugin/beacon-http/listener/<string:listener_uuid>/kill
    """

    @http_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            500: "Server Error",
        },
        description="Kill a running listener by UUID.",
    )
    @http_ns.marshal_with(general_response, code=200)
    @jwt_required()
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


@http_ns.route("")
@http_ns.doc(description="Ping endpoint for basic health checks")
class HttpListenerPingResource(Resource):
    """
    GET /ping
    """

    @http_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    @jwt_required()
    def get(self):
        """
        A super simple, basic upcheck endpoint.
        """
        print(api_response)
        # return api_response(data="pong")
        return "pong"
        # "pong", 200


# ------------------------------------------------------------------------------------
#   Other protocols...
# ------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------
#   4) Register the namespace with your Flask-RESTX Api
#      This is typically done once in your initialization code.
# ------------------------------------------------------------------------------------
Instance().api.add_namespace(listener_manager_ns, path="/listener/manager")
Instance().api.add_namespace(http_ns, path="/listener/http")
