import json

import redis
import requests
from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_restx import Api, Namespace, Resource, fields
from modules.agent import BaseAgent
from modules.config import Config
from modules.instances import Instance
from modules.log import log
from modules.utils import api_response
from redis_om import get_redis_connection

logger = log(__name__)
app = Instance().app


class Info:
    name = "debug"
    author = "ryanq.47"


# ------------------------------------------------------------------------
#                      Create Namespaces + Stuff + Models
# ------------------------------------------------------------------------
debug_ns = Namespace(
    "Plugin: debug",
    description="Debug Plugin endpoints",
)


# ------------------------------------------------------------------------
#                      Debug - Spawn VLMT Clients
# ------------------------------------------------------------------------
# @debug_ns.route("/spawn_agents")
# class DebugSpawnAgentsResource(Resource):
#     @debug_ns.doc(
#         responses={
#             200: "Success",
#             400: "Bad Request",
#             401: "Missing Auth",
#             500: "Server Side error",
#         },
#     )
#     def get(self):
#         """
#         Spawn X "fake" agents, used for testing purposes
#         """
#         r = requests.get("http://127.0.0.1:8081/")

#         return api_response()


# ------------------------------------------------------------------------
#                      Debug - Kill VLMT Clients
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
#                      Debug - Spawn VLMT Listeners
# ------------------------------------------------------------------------
@debug_ns.route("/spawn_listeners")
class DebugSpawnAgentsResource(Resource):
    @debug_ns.doc(
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
        Spawn X listeners, used for testing purposes
        """
        for i in range(0, 5):
            url = "http://127.0.0.1:8081/plugin/file-beacon-v1/listener/spawn"
            data = {"port": 9000 + i, "host": "0.0.0.0"}

            r = requests.post(url=url, json=data)

        return api_response(message="Spawned 5 listeners")


# ------------------------------------------------------------------------
#                      Debug - Kill VLMT Listeners
# ------------------------------------------------------------------------

Instance().api.add_namespace(debug_ns, path="/debug")
