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
    name = "credstore"
    author = "ryanq.47"


# ------------------------------------------------------------------------
#                      Create Namespaces + Stuff + Models
# ------------------------------------------------------------------------
credstore_ns = Namespace(
    "Plugin: credstore",
    description="credstore Plugin endpoints",
)

credstore_response = credstore_ns.model(
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
@credstore_ns.route("/credential/<string:credential_id>")
class StatsAgentsResource(Resource):
    """
    GET /stats/credential/...
    """

    @credstore_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    @credstore_ns.marshal_with(credstore_response, code=200)
    # @jwt_required
    def get(self, credential_id):
        try:
            return api_response(message=credential_id)

        except Exception as e:
            logger.error(e)
            return api_response(status=500)

    def put(self):
        """Put a credential"""
        try:
            return api_response(message="PUT")

        except Exception as e:
            logger.error(e)
            return api_response(status=500)

    def delete(self, credential_id):
        """Delete Credential

        Args:
            credential_id (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            ...
            return api_response(message=credential_id)

        except Exception as e:
            logger.error(e)
            return api_response(status=500)


# ------------------------------------------------------------------------
#                      Stats - Agents
# ------------------------------------------------------------------------
@credstore_ns.route("/credentials")
class StatsAgentsResource(Resource):
    """
    GET /credstore/credentials

    Gets all credentials
    """

    @credstore_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    @credstore_ns.marshal_with(credstore_response, code=200)
    # @jwt_required
    def get(self):
        try:
            ...
            return api_response(message="hi")

        except Exception as e:
            logger.error(e)
            return api_response(status=500)


# 2) Register the namespaces with paths
Instance().api.add_namespace(credstore_ns, path="/credstore")
