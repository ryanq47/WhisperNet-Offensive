import redis
from flask_jwt_extended import jwt_required
from flask_restx import Api, Namespace, Resource
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
#                      Create Namespaces + Stuff
# ------------------------------------------------------------------------
stats_ns = Namespace(
    "Plugin: stats",
    description="BROKEN - Stats Plugin endpoints",
)
ping_ns = Namespace("ping", description="Ping endpoint")


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
    def get(self):
        """
        Get all agents currently registered in the redis DB

        Returns: JSON
        """
        logger.warning("UNAUTH ENDPOINT: Stats/clients")
        try:
            # Fetch all keys with the prefix 'client:' using SCAN
            client_keys = redis_conn.scan_iter("client:*")

            # Dictionary to store client data
            clients_dict = {}

            # Retrieve data for each client key
            for key in client_keys:
                # Use HGETALL to fetch all fields and values from a Redis hash
                client_data = redis_conn.hgetall(key)
                clients_dict[key] = client_data

            return api_response(data=clients_dict)
        except Exception as e:
            logger.error(e)
            return api_response(status=500)


# ------------------------------------------------------------------------
#                      Stats - Plugins
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
# ------------------------------------------------------------------------
@stats_ns.route("/containers")
class StatsContainersResource(Resource):
    """
    GET /stats/containers
    """

    @stats_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    def get(self):
        """Returns JSON of containers that are currently up/serving something"""
        prefix = "container:*"
        container_dict = {"containers": []}

        cursor = 0
        while True:
            cursor, keys = redis_conn.scan(cursor=cursor, match=prefix)
            for key in keys:
                container_data = redis_conn.json().get(key)
                container_dict["containers"].append(container_data)

            if cursor == 0:
                break

        return api_response(data=container_dict)


# ------------------------------------------------------------------------
#                      Ping Endpoint
# ------------------------------------------------------------------------
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
    @jwt_required()
    def get(self):
        """
        A super simple, basic upcheck endpoint.
        """
        return "pong", 200


# 3) Register the namespaces with paths
Instance().api.add_namespace(stats_ns, path="/stats")
Instance().api.add_namespace(ping_ns, path="/ping")
