import json

import redis
from flask import Response
from flask_jwt_extended import jwt_required
from flask_restx import Api, Namespace, Resource, fields
from modules.agent import BaseAgent
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
    name = "stats"
    author = "ryanq.47"


# ------------------------------------------------------------------------
#                      Create Namespaces + Stuff + Models
# ------------------------------------------------------------------------
stats_ns = Namespace(
    "Plugin: stats",
    description="Stats Plugin endpoints",
)
ping_ns = Namespace("ping", description="Ping endpoint")

# Response models for each namespace, allowing for easy tweaks, etc.
ping_response = ping_ns.model(
    "PingResponse",
    {
        "rid": fields.String(description="Request ID"),
        "timestamp": fields.String(description="Request Timestamp, Unix Time"),
        "status": fields.Integer(description="Response Code", default=200),
        "data": fields.String(description="Data from server response", default="pong"),
        "message": fields.String(
            description="Message to go along with data in response"
        ),
    },
)

stats_response = stats_ns.model(
    "StatsResponse",
    {
        "rid": fields.String(description="Request ID"),
        "timestamp": fields.String(description="Request Timestamp, Unix Time"),
        "status": fields.Integer(description="Response Code", default=200),
        "data": fields.Raw(description="Data from server response"),
        "message": fields.String(
            description="Message to go along with data in response"
        ),
    },
)


# ------------------------------------------------------------------------
#                      Stats - Agents
# ------------------------------------------------------------------------
@stats_ns.route("/agents")
class StatsAgentsResource(Resource):
    """
    GET /stats/agents
    """

    @stats_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    @stats_ns.marshal_with(stats_response, code=200)
    @jwt_required()
    def get(self):
        """
        Get all agents currently registered in the redis DB

        Returns: JSON
        Returns all agents + agent data in redis.

        Example Output:
            "{'HCKD:agent:SOMEID_1': {'pk': '01JGX9MT0YRVZZHXYVS26ZT1Z1', 'agent_id': 'SOMEID_1', 'data': {'system': {'hostname': None, 'os': None, 'os_version': None, 'architecture': None, 'username': None, 'privileges': None, 'uptime': None}, 'network': {'internal_ip': None, 'external_ip': None, 'mac_address': None, 'default_gateway': None, 'dns_servers': [], 'domain': None}, 'hardware': {'cpu': None, 'cpu_cores': None, 'ram': None, 'disk_space': None}, 'agent': {'id': 'SOMEID_1', 'version': None, 'first_seen': None, 'last_seen': None}, 'security': {'av_installed': [], 'firewall_status': None, 'sandbox_detected': False, 'debugger_detected': False}, 'geo': {'country': None, 'city': None, 'latitude': None, 'longitude': None}, 'config': {'file': None}}}}"
        """
        try:
            # Fetch all keys with the prefix 'agent:' using SCAN
            # List comp, to catch all keys that only have a segment of 3. This makes sure we catch the keys that only have 3 segments, which are registration keys
            # small oversight in my key naming. All other keys are HCKD:x:x:data or something
            # If I didn't do this, all subkeys under "HCKD:agent:*" would be included in the response
            agent_keys = [
                key
                for key in redis_conn.scan_iter("HCKD:agent:*")
                if len(key.split(":")) == 3
            ]

            agent_data_keys = redis_conn.scan_iter("HCKD:agent:data:*")

            # Dictionary to store client data
            agents_dict = {}
            agents_data_dict = {}

            # Convert agent_data_keys iterator to a list, prevents the generator (scan_iter) from discarding as it loops over
            agent_data_keys = list(redis_conn.scan_iter("HCKD:agent:data:*"))

            # Combining the registration key with the data key
            for key in agent_keys:
                # Use HGETALL to fetch all fields and values from a Redis hash
                # Get the agent key itself, and put it into the key
                agent_registration_data = redis_conn.hgetall(key)
                agents_dict[key] = agent_registration_data

                # For each data key (now a reusable list),
                for data_key in agent_data_keys:
                    # Lookup key data
                    agent_data = redis_conn.hgetall(data_key)
                    agent_data_dict = json.loads(agent_data["json_blob"])
                    if (
                        # Check IDs to make sure the correct data goes into the correct reg key
                        agent_data_dict["agent"]["id"]
                        == agent_registration_data["agent_id"]
                    ):
                        # Get the data key associated with it
                        agents_dict[key]["data"] = agent_data_dict
                        break  # Stop once we find the correct match for this agent_key

            # Example data output
            # "{'HCKD:agent:SOMEID_1': {'pk': '01JGX7R9298ECF43ZJQTK0M0ER', 'agent_id': 'SOMEID_1'}}"
            # IDEA: Add data key, ex:
            # "{'HCKD:agent:SOMEID_1': {'pk': '01JGX7R9298ECF43ZJQTK0M0ER', 'agent_id': 'SOMEID_1'} 'data': data_dict}"
            return api_response(data=agents_dict)

        except Exception as e:
            logger.error(e)
            return api_response(status=500)


@stats_ns.route("/agent/<string:agent_uuid>")
class StatsAgentResource(Resource):
    """
    GET /stats/agents
    """

    @stats_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    @stats_ns.marshal_with(stats_response, code=200)
    @jwt_required()
    def get(self, agent_uuid):
        """
        Get data of ONE agent currently registered in the Redis DB.

        Returns:
            JSON in the specified format.
        """

        try:
            # Sanitize the agent_uuid to allow only alphanumeric characters and hyphens
            if not re.match(r"^[a-zA-Z0-9-]+$", agent_uuid):
                raise ValueError(
                    "Invalid agent_uuid format. Only alphanumeric characters and hyphens are allowed."
                )

            # Fetch agent registration data
            agent_registration_key = f"HCKD:agent:{agent_uuid}"
            agent_registration_data = redis_conn.hgetall(agent_registration_key)

            if not agent_registration_data:
                return api_response(status=404, data={"error": "Agent not found"})

            # No decoding needed, data is already in the correct format
            agent_dict = dict(agent_registration_data)

            # Fetch agent data
            agent_data_key = f"HCKD:agent:data:{agent_uuid}"
            agent_data = redis_conn.hgetall(agent_data_key)

            if agent_data:
                # Parse the JSON blob from Redis
                json_blob = agent_data.get("json_blob")
                agent_data_dict = json.loads(json_blob) if json_blob else {}
            else:
                agent_data_dict = {}

            # Combine registration and data
            agent_dict["data"] = agent_data_dict

            # Construct final output with the registration key
            final_output = {agent_registration_key: agent_dict}

            # Return the response
            return api_response(data=final_output)

        except ValueError as e:
            logger.error(f"Input validation error: {e}")
            return api_response(status=400, data={"error": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return api_response(status=500, data={"error": "Internal Server Error"})


# ------------------------------------------------------------------------
#                      Stats - Listeners
# ------------------------------------------------------------------------
@stats_ns.route("/listeners")
class StatsListenersResource(Resource):
    """
    GET /stats/listeners
    """

    @stats_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    @stats_ns.marshal_with(stats_response, code=200)
    @jwt_required()
    def get(self):
        """
        Get all listeners currently registered in the redis DB.

        Returns: JSON
        """
        try:
            # Fetch all keys with the prefix 'listeners:' using SCAN
            listener_keys = [
                key
                for key in redis_conn.scan_iter("HCKD:listener:*")
                if len(key.split(":")) == 3
            ]

            # Convert the agent_data_keys generator to a list
            agent_data_keys = list(redis_conn.scan_iter("HCKD:listener:data:*"))

            # Dictionary to store client data
            listener_dict = {}

            # Combining the registration key with the data key
            for key in listener_keys:
                # Fetch all fields and values from a Redis hash
                listener_registration_data = redis_conn.hgetall(key)
                listener_dict[key] = listener_registration_data

                # Iterate through the data keys
                for data_key in agent_data_keys:
                    # Lookup key data
                    agent_data = redis_conn.hgetall(data_key)
                    listener_data_dict = json.loads(agent_data["json_blob"])
                    if (
                        listener_data_dict["listener"]["id"]
                        == listener_registration_data["listener_id"]
                    ):
                        # Associate the data key with the listener registration
                        listener_dict[key]["data"] = listener_data_dict
                        break  # Stop searching once the correct match is found

            return api_response(data=listener_dict)

        except Exception as e:
            logger.error(e)
            return api_response(status=500)


@stats_ns.route("/listener/<string:listener_uuid>")
class StatsListenerResource(Resource):
    """
    GET /stats/agents
    """

    @stats_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    @stats_ns.marshal_with(stats_response, code=200)
    @jwt_required()
    def get(self, listener_uuid):
        """
        Get data of ONE agent currently registered in the Redis DB.

        Returns:
            JSON in the specified format.
        """

        try:
            # Sanitize the agent_uuid to allow only alphanumeric characters and hyphens
            if not re.match(r"^[a-zA-Z0-9-]+$", listener_uuid):
                raise ValueError(
                    "Invalid agent_uuid format. Only alphanumeric characters and hyphens are allowed."
                )

            # Fetch agent registration data
            agent_registration_key = f"HCKD:listener:{listener_uuid}"
            agent_registration_data = redis_conn.hgetall(agent_registration_key)

            if not agent_registration_data:
                return api_response(status=404, data={"error": "Agent not found"})

            # No decoding needed, data is already in the correct format
            agent_dict = dict(agent_registration_data)

            # Fetch agent data
            agent_data_key = f"HCKD:listener:data:{listener_uuid}"
            agent_data = redis_conn.hgetall(agent_data_key)

            if agent_data:
                # Parse the JSON blob from Redis
                json_blob = agent_data.get("json_blob")
                agent_data_dict = json.loads(json_blob) if json_blob else {}
            else:
                agent_data_dict = {}

            # Combine registration and data
            agent_dict["data"] = agent_data_dict

            # Construct final output with the registration key
            final_output = {agent_registration_key: agent_dict}

            # Return the response
            return api_response(data=final_output)

        except ValueError as e:
            logger.error(f"Input validation error: {e}")
            return api_response(status=400, data={"error": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return api_response(status=500, data={"error": "Internal Server Error"})


# ------------------------------------------------------------------------
#                      Stats - Agents temp
# ------------------------------------------------------------------------


@stats_ns.route("/agents/commands")
class AgentCommandsResource(Resource):
    """
    GET /agents/commands
    """

    @stats_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    @stats_ns.marshal_with(stats_response, code=200)
    @jwt_required()
    def get(self):
        """
        Get data of ONE agent currently registered in the Redis DB.

        Returns:
            JSON in the specified format.
        """

        try:
            temp_list_of_dicts = [
                {"command": "SOMECOMMAND", "response": "SOMEREPSONSE"},
                {"command": "SOMECOMMAND", "response": "SOMEREPSONSE"},
                {"command": "SOMECOMMAND", "response": "SOMEREPSONSE"},
                {"command": "SOMECOMMAND", "response": "SOMEREPSONSE"},
                {"command": "SOMECOMMAND", "response": "SOMEREPSONSE"},
            ]

            # Return the response
            return api_response(data=temp_list_of_dicts)

        except ValueError as e:
            logger.error(f"Input validation error: {e}")
            return api_response(status=400, data={"error": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return api_response(status=500, data={"error": "Internal Server Error"})


# ------------------------------------------------------------------------
#                      Stats - All
#
# ------------------------------------------------------------------------
@stats_ns.route("/all")
class StatsAllResource(Resource):
    """
    GET /stats/all

    Get all Agents, and Listeners from the server

    Intended to be a safe search, all data in the redis query is returned, and the frontend must handle searching it, not the server
    """

    @stats_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    @stats_ns.marshal_with(stats_response, code=200)
    @jwt_required()
    def get(self):
        """
        Returns a combined JSON object containing both agents and listeners
        in a single top-level dictionary, e.g.:

        {
          "HCKD:agent:AGENT_1": { ... },
          "HCKD:agent:AGENT_2": { ... },
          "HCKD:listener:LISTENER_1": { ... },
          ...
        }
        """
        try:
            # ---------------------------------------------------------------
            #                   Gather Agents
            # ---------------------------------------------------------------
            agent_keys = [
                key
                for key in redis_conn.scan_iter("HCKD:agent:*")
                if len(key.split(":")) == 3
            ]
            # Convert agent_data_keys to a list
            agent_data_keys = list(redis_conn.scan_iter("HCKD:agent:data:*"))

            # Dictionary to store combined agent data
            combined_dict = {}

            for key in agent_keys:
                registration_data = redis_conn.hgetall(key)
                # Convert to a normal dict
                combined_dict[key] = dict(registration_data)

                # Attempt to match with the data key
                for data_key in agent_data_keys:
                    agent_data = redis_conn.hgetall(data_key)
                    if not agent_data:
                        continue
                    agent_data_dict = json.loads(agent_data["json_blob"])
                    if agent_data_dict["agent"]["id"] == registration_data.get(
                        "agent_id"
                    ):
                        combined_dict[key]["data"] = agent_data_dict
                        break  # Found the matching data

            # ---------------------------------------------------------------
            #                   Gather Listeners
            # ---------------------------------------------------------------
            listener_keys = [
                key
                for key in redis_conn.scan_iter("HCKD:listener:*")
                if len(key.split(":")) == 3
            ]
            # Convert listener_data_keys to a list
            listener_data_keys = list(
                redis_conn.scan_iter("HCKD:listener:data:*")
            )

            for key in listener_keys:
                registration_data = redis_conn.hgetall(key)
                combined_dict[key] = dict(registration_data)

                # Attempt to match with the data key
                for data_key in listener_data_keys:
                    listener_data = redis_conn.hgetall(data_key)
                    if not listener_data:
                        continue
                    listener_data_dict = json.loads(listener_data["json_blob"])
                    if listener_data_dict["listener"]["id"] == registration_data.get(
                        "listener_id"
                    ):
                        combined_dict[key]["data"] = listener_data_dict
                        break

            # ---------------------------------------------------------------
            # Return single dictionary (no nesting of "agents"/"listeners")
            # ---------------------------------------------------------------
            return api_response(data=combined_dict)

        except Exception as e:
            logger.error(e)
            return api_response(status=500, data={"error": str(e)})


# ------------------------------------------------------------------------
#                      Stats - Logs
# ------------------------------------------------------------------------


@stats_ns.route("/logs/text")
class StatsLogsResource(Resource):
    """
    GET /stats/logs/text

    Get the logs from the logfile

    Returns a raw contents of logs, ex:
        2025-01-12 16:27:25,846 - stats - WARNING - Stats is broken until redis keys are adjusted
        2025-01-12 16:27:31,976 - stats - WARNING - UNAUTH ENDPOINT: Stats/clients

    """

    @stats_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    # @stats_ns.marshal_with(stats_response, code=200)
    # def get(self):
    #     with open("./HCKD.log", "r") as log_file:
    #         return log_file.read(), 200
    @jwt_required()
    def get(self):
        ANSI_COLOR_REGEX = re.compile(r"\x1B\[[0-9;]*m")

        def generate():
            with open("HCKD.log", "r", encoding="utf-8") as log_file:
                for line in log_file:
                    # Strip out ANSI color codes
                    yield ANSI_COLOR_REGEX.sub("", line)

        return Response(generate(), mimetype="text/plain")


@stats_ns.route("/logs/html")
class StatsHTMLLogsResource(Resource):
    """
    GET /stats/logs/html

    Get the logs from the logfile, formatted in HTML, with color.

    GET /stats/logs

    Get the logs from the logfile

    Returns HTML formatted contents of logs
    """

    @stats_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    # @stats_ns.marshal_with(stats_response, code=200)
    # def get(self):
    #     with open("./HCKD.log", "r") as log_file:
    #         return log_file.read(), 200
    @jwt_required()
    def get(self):
        # Mapping ANSI color codes to CSS styles
        color_map = {
            "0": "color: initial;",  # Reset
            "31": "color: red;",
            "32": "color: green;",
            "33": "color: red;",
            "34": "color: DarkBlue;",
            "35": "color: magenta;",
            "36": "color: blue;",
            "37": "color: white;",
            # Extend as needed...
        }

        # Regex to capture color codes like \x1b[31m (i.e., \x1B\[(digits)m)
        ansi_color_pattern = re.compile(r"\x1B\[(\d+)m")

        def ansi_to_span(match):
            """Converts a single ANSI code into a <span style="...">."""
            code = match.group(1)
            css = color_map.get(code, "")
            return f'<span style="{css}">'

        # Read the entire file
        with open("./HCKD.log", "r", encoding="utf-8") as log_file:
            raw_text = log_file.read()

        # Replace color codes like \x1b[31m with <span style="color:red;">
        converted = ansi_color_pattern.sub(ansi_to_span, raw_text)

        # Replace the reset code \x1b[0m with closing </span>
        # (you can do this repeatedly if logs have multiple resets)
        converted = re.sub(r"\x1B\[0m", "</span>", converted)

        # Wrap the final text in <pre> to preserve spacing and line breaks
        return f"<pre>{converted}</pre>", 200


# ------------------------------------------------------------------------
#                      Stats - Plugins
#               Currently disabled until needed/updated
# ------------------------------------------------------------------------
# @stats_ns.route("/plugins")
# class StatsPluginsResource(Resource):
#     """
#     GET /stats/plugins
#     """

#     @stats_ns.doc(
#         responses={
#             200: "Success",
#             400: "Bad Request",
#             401: "Missing Auth",
#             500: "Server Side error",
#         },
#     )
#     @stats_ns.marshal_with(stats_response, code=200)
#     def get(self):
#         """Returns JSON of plugins that are currently up/serving something"""
#         prefix = "plugin:*"
#         plugins_dict = {"plugins": []}

#         cursor = 0
#         while True:
#             cursor, keys = redis_conn.scan(cursor=cursor, match=prefix)
#             for key in keys:
#                 plugin_data = redis_conn.json().get(key)
#                 plugins_dict["plugins"].append(plugin_data)

#             if cursor == 0:
#                 break

#         return api_response(data=plugins_dict)


# ------------------------------------------------------------------------
#                      Stats - Containers
#               Currently disabled until needed/updated
# ------------------------------------------------------------------------
# @stats_ns.route("/containers")
# class StatsContainersResource(Resource):
#     """
#     GET /stats/containers
#     """

#     @stats_ns.doc(
#         responses={
#             200: "Success",
#             400: "Bad Request",
#             401: "Missing Auth",
#             500: "Server Side error",
#         },
#     )
#     @stats_ns.marshal_with(stats_response, code=200)
#     def get(self):
#         """Returns JSON of containers that are currently up/serving something"""
#         prefix = "container:*"
#         container_dict = {"containers": []}

#         cursor = 0
#         while True:
#             cursor, keys = redis_conn.scan(cursor=cursor, match=prefix)
#             for key in keys:
#                 container_data = redis_conn.json().get(key)
#                 container_dict["containers"].append(container_data)

#             if cursor == 0:
#                 break

#         return api_response(data=container_dict)


# ------------------------------------------------------------------------
#                      Ping Endpoint
# ------------------------------------------------------------------------
# ping_model = ping_ns.model(
#     "PingResponse", {"message": fields.String(description="Response message")}
# )


@ping_ns.route("")
@ping_ns.doc(description="Ping endpoint for basic health checks")
class PingResource(Resource):
    """
    GET /ping
    """

    @ping_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    @ping_ns.marshal_with(ping_response, code=200)
    @jwt_required()
    def get(self):
        """
        A super simple, basic upcheck endpoint.
        """
        print(api_response)
        return api_response(data="pong")
        # "pong", 200


# 2) Register the namespaces with paths
Instance().api.add_namespace(stats_ns, path="/stats")
Instance().api.add_namespace(ping_ns, path="/ping")
