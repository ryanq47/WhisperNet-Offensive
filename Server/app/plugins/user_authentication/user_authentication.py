from flask_restx import Namespace, Resource, fields
from flask import request
import bcrypt
from modules.instances import Instance
from modules.config import Config
from modules.models import User
from sqlalchemy.exc import IntegrityError, NoResultFound
from modules.utils import api_response
from modules.log import log
from modules.utils import generate_unique_id
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    decode_token,
    get_jwt_identity,
)
import datetime

logger = log(__name__)
app = Instance().app


# ------------------------------------
#  Info class (optional metadata)
# ------------------------------------
class Info:
    name = "UserAuthentication"
    author = "ryanq47"


# ------------------------------------
#  Create Namespace & Models
# ------------------------------------
auth_ns = Namespace(
    "Plugin: authentication",
    description="User Authentication endpoints",
)

# This model parallels how 'stats_response' etc. were done
auth_response = auth_ns.model(
    "AuthResponse",
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

# Optionally, you might define an input model for request payload:
login_model = auth_ns.model(
    "LoginModel",
    {
        "username": fields.String(required=True, description="User's username"),
        "password": fields.String(required=True, description="User's password"),
    },
)

register_model = auth_ns.model(
    "RegisterModel",
    {
        "username": fields.String(required=True, description="User's username"),
        "password": fields.String(required=True, description="User's password"),
    },
)


# ------------------------------------
#  /auth/login
# ------------------------------------
@auth_ns.route("/login")
class LoginResource(Resource):
    @auth_ns.expect(login_model)  # optional: requires "username" and "password"
    @auth_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Invalid Credentials",
            500: "Server Side Error",
        },
        description="Endpoint to log in with username/password.",
    )
    @auth_ns.marshal_with(auth_response, code=200)
    def post(self):
        """
        POST /auth/login

        Logs a user in by verifying the provided username & password
        and, on success, returns a JWT token (access_token).
        """
        db = Instance().db_engine
        data = request.get_json()

        if not data or "username" not in data or "password" not in data:
            return api_response(message="Missing username or password"), 400

        username = data["username"]
        password = data["password"]

        try:
            # Attempt to fetch user from DB
            user = User.query.filter_by(username=username).one()
        except NoResultFound:
            logger.debug("No user found with the given username.")
            user = None

        try:
            if user and user.password:
                # Compare the request password with hashed password in DB
                if bcrypt.checkpw(password.encode(), user.password):
                    logger.info(f"{user.uuid}:{user.username} logging in")
                    logger.warning("Hardcoded 1440 (one day) minute token expiration")
                    access_token = create_access_token(
                        identity=user.uuid,
                        expires_delta=datetime.timedelta(minutes=1440),
                    )

                    return api_response(
                        message="Login Success",
                        data={"access_token": access_token},
                        status=200,
                    )
                else:
                    logger.info(f"{username} failed to log in")
                    return api_response(
                        message="Login Failure",
                        data={"access_token": ""},
                        status=401,
                    )
            else:
                # user object is None or user.password is None
                logger.warning(f"User '{username}' not found or invalid in DB.")
                return (
                    api_response(message="Login Failure", data={"access_token": ""}),
                    401,
                )

        except Exception as e:
            logger.error(e)
            return api_response(message="Internal server error"), 500


# ------------------------------------
#  /auth/delete
# ------------------------------------
@auth_ns.route("/delete/<string:user_id>")
class DeleteUserResource(Resource):
    @auth_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            404: "User Not Found",
            409: "Cannot Delete Last User",
            500: "Server Side Error",
        },
        description="Endpoint to delete a user by their ID (requires JWT).",
    )
    @jwt_required()
    def delete(self, user_id):
        """
        DELETE /auth/delete/<user_id>

        Deletes a user with the provided user ID, ensuring at least one user remains in the database.
        """
        db = Instance().db_engine

        try:
            # Check if there's only one user in the database
            total_users = User.query.count()
            if total_users <= 1:
                return (
                    api_response(message="Cannot delete the last user in the database"),
                    409,
                )

            # Get the current user making the request
            current_user_id = get_jwt_identity()

            # Prevent users from deleting themselves
            if current_user_id == user_id:
                return api_response(message="You cannot delete yourself"), 400

            # Fetch the user to delete
            user = User.query.filter_by(uuid=user_id).first()
            if not user:
                return api_response(message="User not found"), 404

            # Delete the user
            db.session.delete(user)
            db.session.commit()

            logger.info(f"User '{user_id}' deleted successfully")
            return api_response(message=f"User '{user.username}' deleted successfully")

        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return api_response(message="Internal server error"), 500

        finally:
            db.session.close()


# ------------------------------------
#  /auth/users
# ------------------------------------
@auth_ns.route("/users")
class ListUsersResource(Resource):
    @auth_ns.doc(
        responses={
            200: "Success",
            500: "Server Side Error",
        },
        description="Endpoint to list all users (requires JWT).",
    )
    @jwt_required()
    def get(self):
        """
        GET /auth/users

        Returns a list of all users in the database.
        """
        db = Instance().db_engine

        try:
            # Fetch all users
            users = User.query.all()
            user_list = [
                {
                    "uuid": user.uuid,
                    "username": user.username,
                }
                for user in users
            ]

            logger.info(f"Listed {len(user_list)} users")
            return api_response(
                message="User list retrieved successfully",
                data={"users": user_list},
            )

        except Exception as e:
            logger.error(e)
            return api_response(message="Internal server error"), 500

        finally:
            db.session.close()


# ------------------------------------
#  /auth/register
# ------------------------------------
@auth_ns.route("/register")
class RegisterResource(Resource):
    @auth_ns.expect(register_model)  #: requires "username" and "password"
    @auth_ns.doc(
        responses={
            201: "Resource Created",
            400: "Bad Request",
            401: "Unauthorized",
            409: "Username Conflict",
            410: "Route Disabled",
            500: "Server Side Error",
        },
        description="Endpoint to register a new user (requires JWT).",
    )
    @auth_ns.marshal_with(auth_response, code=201)
    @jwt_required()
    def post(self):
        """
        POST /auth/register

        Creates a new user, if registrations are enabled in config and
        username is not already taken.
        """
        if not Config().config.server.endpoints.enable_registration:
            return api_response(message="Route is disabled"), 410

        db = Instance().db_engine

        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return api_response(message="username and password are required"), 400

            # Check if user with the same username already exists
            if User.query.filter_by(username=username).first():
                return (
                    api_response(message="A user with this username already exists"),
                    409,
                )

            # Encrypt password
            hashed_password = bcrypt.hashpw(
                password.encode(),
                bcrypt.gensalt(
                    rounds=Config().config.server.authentication.bcrypt.rounds
                ),
            )

            user_id = generate_unique_id()
            new_user = User(
                uuid=user_id,
                username=username,
                password=hashed_password,
            )
            db.session.add(new_user)
            db.session.commit()

            logger.info(f"User '{user_id}':'{username}' has been created")
            return (
                api_response(message=f"User '{username}' created successfully"),
                201,
            ), 201

        except IntegrityError as sqle:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(sqle):
                logger.warning(
                    f"Duplicate username '{username}' attempted registration."
                )
                return (
                    api_response(message="A user with this username already exists"),
                    409,
                )
            return api_response(message="An integrity error occurred"), 400

        except Exception as e:
            db.session.rollback()
            logger.error(e)
            return api_response(message="Internal server error"), 500

        finally:
            db.session.close()


# ------------------------------------
#  Finally, Register the Namespace
# ------------------------------------
Instance().api.add_namespace(auth_ns, path="/auth")
