import json

import redis
from flask import Response, request
from flask_jwt_extended import jwt_required
from flask_restx import Api, Namespace, Resource, fields
from modules.agent import BaseAgent
from plugins.listener.http.agent import Agent
from modules.config import Config
from modules.instances import Instance
from modules.log import log
from modules.utils import api_response
from redis_om import get_redis_connection
import re

logger = log(__name__)

# Get your Flask instance (instead of "app = Flask(__name__)")
app = Instance().app

logger.warning("Stats is broken until redis keys are adjusted")

# Instead of overshadowing the `redis` import, rename your connection object
redis_conn = get_redis_connection(
    host=Config().config.redis.bind.ip,
    port=Config().config.redis.bind.port,
    decode_responses=True,
)


class Info:
    name = "agent"
    author = "ryanq.47"


# ------------------------------------------------------------------------
#                      Create Namespaces + Stuff + Models
# ------------------------------------------------------------------------
agent_ns = Namespace(
    "Plugin: Agents",
    description="Agents Plugin endpoints",
)

# Response models for each namespace, allowing for easy tweaks, etc.
# ping_response = ping_ns.model(
#     "PingResponse",
#     {
#         "rid": fields.String(description="Request ID"),
#         "timestamp": fields.String(description="Request Timestamp, Unix Time"),
#         "status": fields.Integer(description="Response Code", default=200),
#         "data": fields.String(description="Data from server response", default="pong"),
#         "message": fields.String(
#             description="Message to go along with data in response"
#         ),
#     },
# )

# stats_response = stats_ns.model(
#     "StatsResponse",
#     {
#         "rid": fields.String(description="Request ID"),
#         "timestamp": fields.String(description="Request Timestamp, Unix Time"),
#         "status": fields.Integer(description="Response Code", default=200),
#         "data": fields.Raw(description="Data from server response"),
#         "message": fields.String(
#             description="Message to go along with data in response"
#         ),
#     },
# )

command_request_model = agent_ns.model(
    "CommandRequest",
    {
        "command": fields.String(required=True, description="Command to enqueue"),
    },
)

# ------------------------------------------------------------------------
#                      Agent Routes
# ------------------------------------------------------------------------


## MOVE ME TO BEACON_HTTP. TEMP TESTING HERE!!!
@agent_ns.route("/<string:agent_uuid>/command/dequeue")
@agent_ns.doc(description="")
class AgentDequeueCommandResource(Resource):
    """
    GET /ping
    """

    @agent_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    # @ping_ns.marshal_with(ping_response, code=200)
    @jwt_required()
    def get(self, agent_uuid):
        """
        Dequeue a command

        returns: command_id
        """

        a = Agent(agent_id=agent_uuid)
        command = a.dequeue_command()

        print(api_response)
        return api_response(data=command)
        # "pong", 200


@agent_ns.route("/<string:agent_uuid>/command/enqueue")
@agent_ns.doc(description="")
class AgentEnqueueCommandResource(Resource):
    """
    POST /ping
    """

    @agent_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    # @ping_ns.marshal_with(ping_response, code=200)
    @jwt_required()
    @agent_ns.expect(command_request_model)
    def post(self, agent_uuid):
        """
        Enqueue command to agent

        {
            "command":
        }


        returns: command_id
        """
        try:
            data = request.get_json()  # Get JSON data from the request
            if not data or "command" not in data:
                return api_response(message="missing 'command' in message body"), 400

            command = data.get("command", "")
            if command == "":
                return api_response(message="'command' cannot be empty"), 400

            a = Agent(agent_id=agent_uuid)
            command_id = a.enqueue_command(command=command)

            print(api_response)
            return api_response(data=command_id)
        except Exception as e:
            return api_response(message="An error occured"), 500


@agent_ns.route("/<string:agent_uuid>/command/all")
@agent_ns.doc(description="Get all commands and responses for this agent")
class AgentEnqueueCommandResource(Resource):
    """
    ...
    """

    @agent_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    # @ping_ns.marshal_with(ping_response, code=200)
    # @jwt_required
    # @agent_ns.expect(command_request_model)
    @jwt_required()
    def get(self, agent_uuid):
        """
        Enqueue command to agent

        {
            "command":
        }


        returns: command_id
        """
        try:

            a = Agent(agent_id=agent_uuid)
            all_commands = a.get_all_commands_and_responses()

            return api_response(data=all_commands)
        except Exception as e:
            return api_response(message="An error occured"), 500


# 2) Register the namespaces with paths
Instance().api.add_namespace(agent_ns, path="/agent")
