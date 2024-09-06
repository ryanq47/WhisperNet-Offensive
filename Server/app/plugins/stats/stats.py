from flask import jsonify
from modules.instances import Instance
from modules.log import log
from modules.redis_models import Client
import redis
from modules.utils import api_response
from modules.config import Config
from redis_om import get_redis_connection
from flask_jwt_extended import jwt_required
from modules.redis_models import ActiveService

logger = log(__name__)
app = Instance().app

class Info:
    name = "stats"
    author = "ryanq.47"

redis = get_redis_connection(  # switch to config values
    host=Config().config.redis.bind.ip,
    port=Config().config.redis.bind.port,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)


# hackily using redis instead of redis-om because of a weird index error
@app.route('/stats/clients', methods=['GET'])
@jwt_required()
def clients():
    try:
        # Fetch all keys with the prefix 'client:' using SCAN for better performance
        client_keys = redis.scan_iter("client:*")

        # Dictionary to store client data
        clients_dict = {}

        # Retrieve data for each client key
        for key in client_keys:
            # Assuming you're using HashModel, use HGETALL to fetch all fields and values
            client_data = redis.hgetall(key)
            # Store the client data in the dictionary
            clients_dict[key] = client_data
        # Return the dictionary as a JSON response
        return api_response(
            data = clients_dict
        )
    except Exception as e:
        logger.error(e)
        return api_response(
            status=500
        )

@app.route('/ping', methods=['GET'])
@jwt_required
def ping():
    """
        A super simple, basic upcheck ping endpoint

        could also throw a jwt req'd, and use it to check if a token has expired.
            Or... use a diff endopint and check like every 1 sec instead of constatly
    """
    return "pong", 200

@app.route('/stats/services', methods=['GET'])
def services():
    '''returns json of plugins that are currently up/serving something'''

    prefix = "service:*"
    # Initialize the dictionary to store results
    active_services = {"active_services": []}

    # Using SCAN to find all keys that match the prefix
    cursor = 0
    while True:
        cursor, keys = redis.scan(cursor=cursor, match=prefix)
        for key in keys:
            # Fetch the data for each key using JSON.GET assuming the data is stored as JSON
            service_data = redis.json().get(key)
                # Append the fetched data to the list in the dictionary
            active_services["active_services"].append(service_data)

        if cursor == 0:
            break

    # format into formj
    # send back
    return api_response(
        data=active_services
    )

@app.route('/stats/plugins', methods=['GET'])
def plugins():
    '''returns json of plugins that are currently up/serving something'''

    prefix = "plugins:*"
    # Initialize the dictionary to store results
    plugins_dict = {"plugins": []}

    # Using SCAN to find all keys that match the prefix
    cursor = 0
    while True:
        cursor, keys = redis.scan(cursor=cursor, match=prefix)
        for key in keys:
            # Fetch the data for each key using JSON.GET assuming the data is stored as JSON
            plugin_data = redis.json().get(key)
                # Append the fetched data to the list in the dictionary
            plugins_dict["plugins"].append(plugin_data)

        if cursor == 0:
            break

    # format into formj
    # send back
    return api_response(
        data=plugins_dict
    )

