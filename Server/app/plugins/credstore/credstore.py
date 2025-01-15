import json

import redis
from flask import Response, request
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

credential_model = credstore_ns.model(
    "Credential",
    {
        "username": fields.String(
            required=True, description="The username for the credential"
        ),
        "password": fields.String(
            required=True, description="The password for the credential"
        ),
        "realm": fields.String(required=False, description="The realm or domain"),
        "notes": fields.String(required=False, description="Additional notes"),
    },
)


# ------------------------------------------------------------------------
#                      Cred - /credential
# ------------------------------------------------------------------------
@credstore_ns.route("/credential")
class CredstoreCredentialResource(Resource):
    """
    GET /stats/credential/
    """

    @credstore_ns.marshal_with(credstore_response, code=200)
    @credstore_ns.expect(credential_model)  # Attach the model here
    def put(self):
        """
        Add a credential to the credential list via a JSON payload.

        Expected JSON Structure:
        {
            "username": "string",
            "password": "string",
            "realm": "string (optional)",
            "notes": "string (optional)"
        }

        Returns:
            dict: Response message with success or error status.
        """
        try:
            # Parse JSON payload
            payload = request.json
            if not payload:
                return api_response(status=400, message="Missing JSON payload")

            username = payload.get("username")
            password = payload.get("password")
            realm = payload.get("realm")
            notes = payload.get("notes")

            # Validate required fields
            if not username or not password:
                return api_response(
                    status=400, message="Username and Password are required"
                )

            # Add credential using the CredStore method
            c = CredStore()
            c.add_credential(
                username=username, password=password, realm=realm, notes=notes
            )

            return api_response(message="Credential added successfully", status=201)

        except Exception as e:
            logger.error(f"Error adding credential: {e}")
            return api_response(status=500, message="Internal Server Error")


# ------------------------------------------------------------------------
#                      Cred - /credential/ID
# ------------------------------------------------------------------------
@credstore_ns.route("/credential/<string:credential_id>")
class CredstoreCredentialResource(Resource):
    """
    GET /stats/credential/ID
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

    @credstore_ns.marshal_with(credstore_response, code=200)
    def delete(self, credential_id):
        """Delete Credential

        Args:
            credential_id (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            c = CredStore()
            c.delete_credential(credential_id=credential_id)
            return api_response(message=f"{credential_id} Deleted successfully")

        except Exception as e:
            logger.error(e)
            return api_response(status=500)


# ------------------------------------------------------------------------
#                      Cred - /credentials
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
