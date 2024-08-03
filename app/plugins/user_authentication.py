from flask import request, jsonify
from modules.instances import Instance
from modules.config import Config


class Info:
    name = "UserAuthentication"
    author = "ryanq47"
    classname = "Login"


class Login:
    """
    Login class for login stuff

    """

    def __init__(self):
        self.app = Instance().app

        self.app.route(f"/login", methods=["GET"])(self.login)

    def login(self):
        return jsonify(
            {"instance": str(Instance().app), "config": str(Config().launch_path)}
        )
        # data = request.get_json()
        # username = data["username"]
        # password = data["password"]
        # print("Received data:", username, password)

        # user = User.query.filter_by(username=username).first()

        # if user and bcrypt.check_password_hash(user.password, password):
        #    access_token = create_access_token(identity=user.id)
        #    return jsonify({"message": "Login Success", "access_token": access_token})
        # else:
        #    return jsonify({"message": "Login Failed"}), 401
