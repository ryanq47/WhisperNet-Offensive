from flask import request, jsonify
import bcrypt
from modules.instances import Instance
from modules.config import Config
from modules.models import User, Token
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, NoResultFound
from modules.utils import api_response
from modules.log import log
from modules.utils import generate_unique_id
from flask_jwt_extended import create_access_token

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
        db = Instance().db_engine

        data = request.get_json()
        username = data["username"]
        password = data["password"]

        try:
            user = User.query.filter_by(username=username).one()
        except NoResultFound:
            logger.debug("No user found with the given username.")
            user = None

        try:
            if user:
                # checking things needed to actually log in
                conditions = [
                    user.username is not None and user.username != "",
                    user.password is not None and user.password != "",
                    user.uuid is not None
                ]

                # user.password gets password feild from db, comps to password entered in request. 
                # this *could* allow for a null password, if the bcrypt lib doesn't spit an error.  
                # or the above check fails for whatever reason. Just something to keep in mind

                # Note, checkpw takes password inputted, and password to check against.
                if bcrypt.checkpw(password.encode(), user.password):
                    logger.info(f"{user.uuid}:{user.username} logging in")
                    logger.debug(f"Creating token for user {user.uuid}")
                    access_token = create_access_token(identity=user.uuid)
                    # replave with better response
                    #return jsonify({"message": "Login Success", "access_token": access_token})
                
                    logger.debug(f"Adding token to db for user {user.uuid}")
                    # store/track that access token now
                    # I actually fucking love ORMs
                    new_token = Token(
                        uuid = user.uuid,
                        token = access_token
                    )
                    db.session.add(new_token)
                    db.session.commit()

                    return api_response(
                        message="Login Success",
                        data={"access_token":access_token}
                    )
                
                else:
                    #logger.info("%s:%s failed to log in", user.id, user.username)# will fail if no results, 
                    # need to use user inputted values 
                    logger.info(f"{username} failed to log in")
                    
                    return api_response(
                        message="Login Failure",
                        data={"access_token":""}
                    )
            
            else:
                logger.warning("User '%s' tried to log in, but was not found.", username)
                return api_response(
                    message="Login Failure",
                    data={"access_token":""}
                )

        except Exception as e:
            logger.error(e)
            raise e

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
                uuid=user_id,
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
