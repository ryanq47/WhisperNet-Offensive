"""
A file-based beacon.

Comms:
 - FormJ


"""

import json
import time
import traceback

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from modules.audit import Audit
from modules.config import Config
from modules.form_j import FormJ
from modules.instances import Instance
from modules.log import log
from modules.redis_models import Client
from modules.utils import api_response
from plugins.simple_http.modules.redis_models import FormJModel
from plugins.simple_http.modules.redis_queue import RedisQueue
from redis.commands.json.path import Path
from redis_om import HashModel, NotFoundError, get_redis_connection

logger = log(__name__)
# app = Instance().app

redis = get_redis_connection(  # switch to config values
    host=Config().config.redis.bind.ip,
    port=Config().config.redis.bind.port,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)


class Info:
    name = "file-beacon-v1"
    author = "ryanq.47"


# Optional route example
@app.route(f"/balls", methods=["GET"])
def myfunctionfromhell():
    return jsonify({"somekey": "somevalue"})


# if __name__ == "__main__":


## Spawn function to be called
def spawn(port, host, nickname=None):
    try:
        logger.debug("Starting file-beacon-v1")
        app.run(debug=True, port=8082, host="0.0.0.0")

    except Exception as e:
        print(e)
