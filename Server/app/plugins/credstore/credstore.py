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
from modules.credstore import CredStore
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
class CredstoreCredentialResource(Resource):
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
            c = CredStore()
            single_cred = c.get_credential(credential_id=credential_id)
            cred_list = serialize_credentials(single_cred)

            return api_response(message="Success", data={"credentials": cred_list})

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
class CredentialsResource(Resource):
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
        """
        Retrieve all credentials and return as a JSON-compatible dictionary
        """
        try:
            c = CredStore()
            all_creds = c.get_all_credentials()
            cred_list = serialize_credentials(all_creds)

            # Return the credentials in a structured response
            return api_response(message="Success", data={"credentials": cred_list})

        except Exception as e:
            logger.error(f"Error retrieving credentials: {e}")
            return api_response(status=500, message="Internal Server Error")


def serialize_credentials(credentials):
    """
    Convert a list of credential objects into a list of dictionaries.

    Args:
        credentials (list): List of credential objects with attributes
            like id, username, password, realm, notes, and date_added.

    Returns:
        list: List of dictionaries representing the credentials.

    Example output:
        {
            "status": 200,
            "message": "Success",
            "data": {
                "credentials": [
                    {
                        "id": 1,
                        "username": "user1",
                        "password": "password1",
                        "realm": "example.com",
                        "notes": "First entry",
                        "date_added": "2025-01-15 12:00:00"
                    },
                    {
                        "id": 2,
                        "username": "user2",
                        "password": "password2",
                        "realm": "example.org",
                        "notes": "Second entry",
                        "date_added": "2025-01-15 13:00:00"
                    }
                ]
            }
        }

    """
    serialized = []
    for cred in credentials:
        serialized.append(
            {
                "id": cred.id,
                "username": cred.username,
                "password": cred.password,
                "realm": cred.realm,
                "notes": cred.notes,
                "date_added": (
                    cred.date_added.strftime("%Y-%m-%d %H:%M:%S")
                    if cred.date_added
                    else None
                ),
            }
        )
    return serialized


# 2) Register the namespaces with paths
Instance().api.add_namespace(credstore_ns, path="/credstore")
