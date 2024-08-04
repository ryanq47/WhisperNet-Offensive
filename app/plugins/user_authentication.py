from flask import request, jsonify
import bcrypt
from modules.instances import Instance
from modules.config import Config
from modules.models import User
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from modules.utils import api_response
from modules.log import log
from modules.utils import generate_unique_id

logger = log(__name__)


class Info:
    name = "UserAuthentication"
    author = "ryanq47"
    classname = "UserManagement"


class UserManagement:
    """
    user class for user stuff

    """

    def __init__(self):
        self.app = Instance().app

        self.app.route(f"/login", methods=["POST"])(self.login)
        self.app.route(f"/register", methods=["POST"])(self.register)

    def login(self):
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        print("Received data:", username, password)
        return "{}", 200

        # user = User.query.filter_by(username=username).first()

        # if user and bcrypt.check_password_hash(user.password, password):
        #    access_token = create_access_token(identity=user.id)
        #    return jsonify({"message": "Login Success", "access_token": access_token})
        # else:
        #    return jsonify({"message": "Login Failed"}), 401

    def register(self):
        db = Instance().db_engine

        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password").encode()  # Put into bytes for bcrypt

            if not all([username, password]):
                return api_response(
                    message="username and password field are required", status=400
                )  # other error

            # check if user exists BEFORE doing computation heavy ops. cuts down a few hundred MS due to bcrypt
            if User.query.filter_by(username=username).first():
                return api_response(
                    message="A user with this username already exists", status=409
                )

            # Now that we are sure the parameters are correct, move onto more heavy computation stuff
            hashed_password = bcrypt.hashpw(
                password,
                bcrypt.gensalt(
                    rounds=Config().config.server.authentication.bcrypt.rounds
                ),
            )
            user_id = generate_unique_id()

            new_user = User(
                id=user_id,
                username=username,
                password=hashed_password,
                authenticated=True,
            )
            db.session.add(new_user)
            db.session.commit()

            logger.info(f"User '{user_id}':'{username}' has been created")
            return api_response(
                message=f"User '{username}' created successfully", status=200
            )

        except IntegrityError as sqle:  # sqlalchemy integ error
            db.session.rollback()

            # Check if the error is related to a UNIQUE constraint violation
            if "UNIQUE constraint failed" in str(sqle):
                logger.warning(
                    f"Duplicate username '{username}' detected on user registration."
                )
                return api_response(
                    message="A user with this username already exists", status=409
                )  # 409 conflict

            return api_response(
                message="An integrity error occured", status=400
            )  # other error

        except Exception as e:
            db.session.rollback()
            logger.error(e)
            raise e

        finally:
            db.session.close()
