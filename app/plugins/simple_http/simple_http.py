from flask import jsonify
from modules.instances import Instance
from modules.log import log

logger = log(__name__)
app = Instance().app


class Info:
    name = "simple_http"
    author = "ryanq.47"


# Optional route example
@app.route("/get/<client_id>", methods=["GET"])
def simple_http_get(client_id):
    return jsonify({"client_id": f"{client_id}"})


@app.route("/post/<client_id>", methods=["POST"])
def simple_http_post(client_id):
    return jsonify({"client_id": f"{client_id}"})
