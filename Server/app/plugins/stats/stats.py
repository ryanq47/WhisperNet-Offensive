import redis
from flask_jwt_extended import jwt_required
from flask_restx import Api, Namespace, Resource, fields
from modules.agent import BaseAgent
from modules.config import Config
from modules.instances import Instance
from modules.log import log
from modules.utils import api_response
from redis_om import get_redis_connection

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
    description="BROKEN - Stats Plugin endpoints",
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
        "data": fields.String(description="Data from server response"),
        "message": fields.String(
            description="Message to go along with data in response"
        ),
    },
)


# ------------------------------------------------------------------------
#                      Stats - Agents
# ------------------------------------------------------------------------
@stats_ns.route("/agents")
class StatsClientsResource(Resource):
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
    def get(self):
        """
        Get all agents currently registered in the redis DB

        Returns: JSON
        Returns all agents in redis. Does NOT return the data associated with each agent

        Example Output:
            {'whispernet:agent:SOMEID_1': {'pk': '01JGX7R9298ECF43ZJQTK0M0ER', 'agent_id': 'SOMEID_1'}}
        """
        logger.warning("UNAUTH ENDPOINT: Stats/clients")
        try:
            # Fetch all keys with the prefix 'agent:' using SCAN
            agent_keys = redis_conn.scan_iter("whispernet:agent:*")

            # Dictionary to store client data
            agents_dict = {}

            # Retrieve data for each client key
            for key in agent_keys:
                # Use HGETALL to fetch all fields and values from a Redis hash
                agent_data = redis_conn.hgetall(key)
                agents_dict[key] = agent_data

            # Example data output
            # "{'whispernet:agent:SOMEID_1': {'pk': '01JGX7R9298ECF43ZJQTK0M0ER', 'agent_id': 'SOMEID_1'}}"
            # IDEA: Add data key, ex:
            # "{'whispernet:agent:SOMEID_1': {'pk': '01JGX7R9298ECF43ZJQTK0M0ER', 'agent_id': 'SOMEID_1'} 'data': data_dict}"

            return api_response(data=agents_dict)
        except Exception as e:
            logger.error(e)
            return api_response(status=500)


# ------------------------------------------------------------------------
#                      Stats - Listeners
# ------------------------------------------------------------------------
@stats_ns.route("/listeners")
class StatsPluginsResource(Resource):
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
    def get(self):
        """
        Get all listeners currently registered in the redis DB

        Returns: JSON
        Returns all listener in redis. Does NOT return the data associated with each listener

        Example Output:
            "{'whispernet:listener:2c877a2b-8a47-476b-86be-a2b4b3bc0de7': {'pk': '01JGX7QZ46DT43K7FPZC1HRYNY', 'listener_id': '2c877a2b-8a47-476b-86be-a2b4b3bc0de7', 'name': 'QUICK_SHARK'}}",
        """
        logger.warning("UNAUTH ENDPOINT: Stats/plugins")
        try:
            # Fetch all keys with the prefix 'agent:' using SCAN
            agent_keys = redis_conn.scan_iter("whispernet:listener:*")

            # Dictionary to store client data
            listeners_dict = {}

            # Retrieve data for each client key
            for key in agent_keys:
                # Use HGETALL to fetch all fields and values from a Redis hash
                listener_data = redis_conn.hgetall(key)
                listeners_dict[key] = listener_data

            # Example data output
            # "{'whispernet:agent:SOMEID_1': {'pk': '01JGX7R9298ECF43ZJQTK0M0ER', 'agent_id': 'SOMEID_1'}}"
            # IDEA: Add data key, ex:
            # "{'whispernet:agent:SOMEID_1': {'pk': '01JGX7R9298ECF43ZJQTK0M0ER', 'agent_id': 'SOMEID_1'} 'data': data_dict}"

            return api_response(data=listeners_dict)
        except Exception as e:
            logger.error(e)
            return api_response(status=500)


# ------------------------------------------------------------------------
#                      Stats - Plugins
#               Currently disabled until needed/updated
# ------------------------------------------------------------------------
@stats_ns.route("/plugins")
class StatsPluginsResource(Resource):
    """
    GET /stats/plugins
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
    def get(self):
        """Returns JSON of plugins that are currently up/serving something"""
        prefix = "plugin:*"
        plugins_dict = {"plugins": []}

        cursor = 0
        while True:
            cursor, keys = redis_conn.scan(cursor=cursor, match=prefix)
            for key in keys:
                plugin_data = redis_conn.json().get(key)
                plugins_dict["plugins"].append(plugin_data)

            if cursor == 0:
                break

        return api_response(data=plugins_dict)


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
    # @jwt_required()
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
