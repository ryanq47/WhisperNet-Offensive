# file: app.py
from flask import Flask
from flask_restx import Api, Namespace, Resource, fields
from waitress import serve

app = Flask("MYSECONDAPP")
api = Api(
    app,
    version="1.0",
    title="My API",
    description="Whispernet HTTP Endpoint",
    doc="/docs",
)

# ------------------------------------------------------------------------------------
#   Namespace
# ------------------------------------------------------------------------------------


# 1) Create Namespace
beacon_http_ns = Namespace("Example: GET/POST", description="GET and POST demo")

# 2) Example data
json_response = {"command": "shell", "args": "whoami /all"}

# ------------------------------------------------------------------------------------
#  Models
# ------------------------------------------------------------------------------------


# 3) Define models
post_input_model = beacon_http_ns.model(
    "PostInput",
    {
        "anyKey": fields.Raw(
            required=False, description="Example of any posted key-value"
        )
    },
)
post_output_model = beacon_http_ns.model(
    "PostOutput",
    {
        "status": fields.String(description="Status of the operation"),
        "data": fields.Raw(description="The received data"),
    },
)


# ------------------------------------------------------------------------------------
#   Resources/Endpoints
# ------------------------------------------------------------------------------------


@beacon_http_ns.route("/get")
class GetResource(Resource):
    def get(self):
        """Returns a predefined JSON response."""

        # get client id

        # spawn base or whatever

        # Get info from redis, pop command

        # format, send off

        response_dict = {"command": "shell", "args": "whoami /all"}

        return json_response, 200


@beacon_http_ns.route("/post")
class PostResource(Resource):
    @beacon_http_ns.expect(post_input_model)
    @beacon_http_ns.marshal_with(post_output_model)
    def post(self):
        """Receives JSON data and returns it in a response."""
        data = beacon_http_ns.payload
        print("Received POST data:", data)
        return {"status": "received", "data": data}, 200


# 5) Register the Namespace
api.add_namespace(beacon_http_ns, path="/")


def run_app(host, port):
    """
    Run the Flask-RESTX application on the given host/port.

    Use waitress to serve.
    """
    serve(app, host=host, port=port)

    # app.run(host=host, port=port, debug=False)


# If you run `python app.py` directly, it defaults to 5000
if __name__ == "__main__":
    run_app()  # same as run_app("0.0.0.0", 5000)
