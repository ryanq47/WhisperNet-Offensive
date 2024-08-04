from flask import request, jsonify
from modules.instances import Instance
from modules.config import Config
from modules.models import User
from flask_sqlalchemy import SQLAlchemy


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

        new_user = User(
            user_id="example@example.com", password="hashedpassword", authenticated=True
        )
        db.session.add(new_user)
        db.session.commit()
        return "", 200
