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
from plugins.build.modules.build_interface import HttpBuildInterface

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
    name = "build"
    author = "ryanq.47"


# ------------------------------------------------------------------------------------
#   1) Create a dedicated Namespace for the Beacon HTTP plugin
# ------------------------------------------------------------------------------------
build_ns = Namespace(
    "Plugin: build",
    description="Build plugin for agents",
)

# ------------------------------------------------------------------------------------
#   2) Define a standard response model (similar to stats_response in your example)
# ------------------------------------------------------------------------------------
build_response = build_ns.model(
    "BuildResponse",
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


@build_ns.route("/<string:agent_type>/build")
class BeaconHttpListenerSpawnResource(Resource):
    """
    POST /plugin/beacon-http/listener/spawn
    """

    @build_ns.marshal_with(build_response, code=200)
    # @jwt_required
    def post(self, agent_type):
        """Post a new build job"""
        # data = request.get_json() or {}
        # listener_port = data.get("port")
        # listener_host = data.get("host")
        # listener_name = data.get("name")

        build_job = HttpBuildInterface("exe_x64")

        build_id = build_job.build()

        build_response_dict = {
            "build_id": build_id,
        }

        return api_response(data=build_response_dict)


# ------------------------------------------------------------------------------------
#   4) Register the namespace with your Flask-RESTX Api
#      This is typically done once in your initialization code.
# ------------------------------------------------------------------------------------
Instance().api.add_namespace(build_ns, path="/plugin/build")
