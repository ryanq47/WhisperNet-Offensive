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
from modules.agent_script_interpreter import AgentScriptInterpreter
from modules.redis_models import AgentCommand

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
        # This might be cooked - is way slower now? May not be this code, might be sleep time
        try:
            data = request.get_json()  # Get JSON data from the request
            if not data or "command" not in data:
                return api_response(message="missing 'command' in message body"), 400

            command = data.get("command", "")
            if command == "":
                return api_response(message="'command' cannot be empty"), 400

            a = Agent(agent_id=agent_uuid)

            ##########
            # Script Stuff
            ##########
            ## old code that fails if no script is loaded.
            #     logger.debug(f"Command inbound from server: {command}")

            #     # check if a script is even registerd to the agent
            #     command_script_name = a.get_command_script()
            #     asi = AgentScriptInterpreter(
            #         script_name=command_script_name,
            #         agent_id=agent_uuid,
            #         # "/home/kali/Documents/GitHub/WhisperNet-Offensive/Server/data/scripts/script1.yaml"
            #     )
            #     command_results = asi.process_command(command)

            #     # if command found in script...
            #     if command_results:
            #         logger.debug("Successful execution of commands")
            #         return api_response(data="Extension Script Command queued")

            #     else:
            #         logger.debug("No script registered for agent")

            #         # queue command normally if not in script
            #         a = Agent(agent_id=agent_uuid)
            #         command_id = a.enqueue_command(command=command)

            #         # print(api_response)
            #         return api_response(data=command_id), 200

            # except Exception as e:
            #     logger.error(e)
            #     return api_response(message="An error occured"), 500

            ## this fixes it.
            logger.debug(f"Command inbound from server: {command}")

            # check if a script is even registerd to the agent
            command_script_name = a.get_command_script()
            if command_script_name != None:
                asi = AgentScriptInterpreter(
                    script_name=command_script_name,
                    agent_id=agent_uuid,
                    # "/home/kali/Documents/GitHub/WhisperNet-Offensive/Server/data/scripts/script1.yaml"
                )
                command_results = asi.process_command(command)

                # if command found in script...
                if command_results:
                    logger.debug("Successful execution of commands")
                    return api_response(data="Extension Script Command queued")

            else:
                logger.debug("No script registered for agent")

            # queue command normally if not in script
            a = Agent(agent_id=agent_uuid)
            command_id = a.enqueue_command(command=command)

            # print(api_response)
            return api_response(data=command_id), 200

        except Exception as e:
            logger.error(e)
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
            logger.error(e)
            return api_response(message="An error occured"), 500


@agent_ns.route("/command/<string:command_uuid>")
@agent_ns.doc(description="Get one command, searching from all the agents")
class AgentGetOneCommandFromAllResource(Resource):
    """
    Searches all agent commands for ONE command, identified by UUID
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
    def get(self, command_uuid):
        try:

            # manual redis search here for UUID, and arragnign of data.
            # This is manual as it searches ALL of redis for the key, not just one agent, like baseagent would
            agent_command = AgentCommand.get(command_uuid)
            if agent_command:
                agent_dict = {
                    "command_id": agent_command.command_id,
                    "command": agent_command.command,
                    "response": (
                        agent_command.response if agent_command.response else None
                    ),
                    "timestamp": agent_command.timestamp,
                    "agent_id": agent_command.agent_id,
                }

            if agent_command:
                return api_response(data=agent_dict)
            else:
                return api_response(data="No results found for command")

        except Exception as e:
            logger.error(e)
            return api_response(message="An error occured"), 500


@agent_ns.route("/<string:agent_uuid>/command-script/register")
@agent_ns.doc(description="Register a command script to this agent")
class AgentUploadCommandScriptResource(Resource):
    """

    JSON:

    {
        "command_script": "scriptname.yaml"
    }

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
    def post(self, agent_uuid):
        """
        Tell which script for the agent to use.

        JSON:

        {
            "command_script": "scriptname.py"
        }

        """
        try:
            data = request.get_json()  # Get JSON data from the request
            if not data or "command_script" not in data:
                return (
                    api_response(message="missing 'command_script' in message body"),
                    400,
                )

            command_script = data.get("command_script", "")
            # if command_script == "":
            #     return api_response(message="'command_script' cannot be empty"), 400

            a = Agent(agent_id=agent_uuid)
            a.set_command_script(command_script)

            return api_response(message="Script registered successfully")
        except Exception as e:
            logger.error(e)
            return api_response(message="An error occured"), 500


# 2) Register the namespaces with paths
Instance().api.add_namespace(agent_ns, path="/agent")
