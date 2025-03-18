# file: app.py
from flask import Flask, request
from flask_restx import Api, Namespace, Resource, fields
from waitress import serve
from modules.config import Config
from plugins.listener.http.agent import Agent
from modules.utils import get_utc_datetime
from modules.log import log  # Import the logger

logger = log(__name__)

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

beacon_http_ns = Namespace("Example: GET/POST", description="GET and POST demo")

# ------------------------------------------------------------------------------------
#   Models
# ------------------------------------------------------------------------------------

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


@beacon_http_ns.route("/get/<string:agent_uuid>")
@beacon_http_ns.doc(description="")
class AgentDequeueCommandResource(Resource):
    def get(self, agent_uuid):
        """
        Dequeue a command

        Returns:
            JSON: {"command": <command>, "args": <args>}
        """
        try:
            a = Agent(agent_id=agent_uuid)
            update_last_seen(agent_class=a)
            command_object = a.dequeue_command()

            # Check if no command was dequeued
            if not command_object:
                return {"command": None, "args": None}

            command = command_object.command
            command_id = command_object.command_id

            # Ensure command is a string
            if not command or not isinstance(command, str):
                return {"command": None, "args": None}

            # Split command into parts
            parts = command.strip().split(" ", 1)
            command_name = parts[0]
            args = parts[1] if len(parts) > 1 else ""

            response_dict = {
                "command_id": command_id,
                "command": command_name,
                "args": args,
            }
            return response_dict
        except Exception as e:
            logger.error("Error in GET endpoint: %s", str(e))
            return "", 500


@beacon_http_ns.route("/post/<string:agent_uuid>")
class PostResource(Resource):
    def post(self, agent_uuid):
        """Receives JSON data and returns it in a response."""
        try:
            # Retrieve payload using the namespace's payload attribute
            response = beacon_http_ns.payload

            # Extract required fields
            command_id = response.get("command_id")
            data = response.get("command_result_data")

            if command_id is None or data is None:
                logger.error(
                    "Missing 'command_id' or 'command_result_data' in payload."
                )
                return {"error": "Missing required fields."}, 400

            # Store the response
            agent = Agent(agent_uuid)
            agent.store_response(command_id, data)

            return {"status": "received", "data": data}, 200

        except Exception as e:
            logger.error("Internal Server Error in POST endpoint: %s", str(e))
            return {"error": "Internal server error."}, 500


# ------------------------------------------------------------------------------------
#   Register Namespace
# ------------------------------------------------------------------------------------

api.add_namespace(beacon_http_ns, path="/")


def run_app(host, port):
    """
    Run the Flask-RESTX application on the given host/port.

    Use waitress to serve.
    """
    serve(app, host=host, port=port)


def update_last_seen(agent_class):
    """
    Updates the last time an agent was seen.
    Triggers on GET request.

    Currently uses UTC datetime.
    """
    agent_class.data.agent.last_seen = str(get_utc_datetime())
    agent_class.unload_data()


if __name__ == "__main__":
    run_app("0.0.0.0", 5000)
