from flask import jsonify
from modules.instances import Instance
from modules.log import log


logger = log(__name__)
app = Instance().app

class Info:
    name = "UserAuthentication"
    author = "ryanq47"

# Optional route example
@app.route('/someroute', methods=['GET'])
def plugin_route():
    return jsonify({"somekey": "somevalue"})