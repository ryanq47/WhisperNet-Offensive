from flask import jsonify
from modules.instances import Instance
from modules.log import log
from modules.redis_models import Client
import redis
from modules.utils import api_response
from modules.config import Config
from redis_om import get_redis_connection
from flask_jwt_extended import jwt_required
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
@app.route('/clients', methods=['GET'])
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