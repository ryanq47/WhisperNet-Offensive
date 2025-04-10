# file: app.py
from flask import Flask, request
from flask_restx import Api, Namespace, Resource, fields
from waitress import serve
from modules.config import Config
from plugins.listener.http.agent import Agent
from modules.utils import get_utc_datetime
from modules.log import log  # Import the logger
import socketio  # Synchronous Socket.IO client
import argparse
import logging

logger = log(__name__)

app = Flask("MYSECONDAPP")
api = Api(
    app,
    version="1.0",
    title="My API",
    description="Whispernet HTTP Endpoint",
    doc="/docs",
)

# --------------------
# Create Socket.IO Client
# --------------------
# This is our synchronous Socket.IO client that will emit events when needed.
ws = socketio.Client()

# Connect to the websocket server on the /shell namespace.
# Adjust the URL and namespace as required.
# ws.connect("http://127.0.0.1:8081", namespaces=["/shell"])


def connect_to_websocket():
    """
    Separate function, putting globally causes it
    to try to conenct to server before WS is up due to imports
    """
    if not ws.connected:
        try:
            ws.connect("http://127.0.0.1:8081", namespaces=["/shell"])
            logger.debug("WebSocket connected on /shell namespace.")
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")


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
@beacon_http_ns.route("/get/<string:agent_id>")
@beacon_http_ns.doc(description="")
class AgentDequeueCommandResource(Resource):
    def get(self, agent_id):
        """
        Dequeue a command

        Returns:
            JSON: {"command": <command>, "args": <args>}
        """
        logger.debug(f"Agent {agent_id} checked in.")

        try:
            a = Agent(agent_id=agent_id)
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

            # --------------
            # Emit agent checked in
            # --------------
            connect_to_websocket()
            if ws.connected:
                # Emit join event so the listener for this agent joins its room.
                logger.debug(f"Emitting join for agent: {agent_id}")
                ws.emit("join", {"agent_id": agent_id}, namespace="/shell")
                # Emit the response to the room corresponding to this agent.
                logger.debug(f"Emitting response to room: {agent_id}")
                ws.emit(
                    "on_agent_connect",
                    {"agent_id": agent_id},
                    namespace="/shell",
                )

            else:
                logger.error("WebSocket client not connected.")

            response_dict = {
                "command_id": command_id,
                "command": command_name,
                "args": args,
            }
            return response_dict
        except Exception as e:
            logger.error("Error in GET endpoint: %s", str(e))
            return "", 500


@beacon_http_ns.route("/post/<string:agent_id>")
class PostResource(Resource):
    def post(self, agent_id):
        """Receives JSON data, stores it in Redis, and emits it via WebSocket."""
        logger.debug(f"Agent {agent_id} posted data")
        try:
            # Ensure the websocket connection is active.
            connect_to_websocket()

            # Retrieve the payload from the namespace's payload attribute.
            response = beacon_http_ns.payload

            # Extract fields from the payload.
            command_id = response.get("command_id")
            data = response.get("command_result_data")

            if data is None:
                logger.warning("Missing 'command_result_data' in payload.")
                return {"error": "Missing required field: command_result_data."}, 400

            # Emit the message via the WebSocket.
            logger.debug("BEFORE WEBSOCKET")
            if ws.connected:
                # Emit join event so the listener for this agent joins its room.
                logger.debug(f"Emitting join for agent: {agent_id}")
                ws.emit("join", {"agent_id": agent_id}, namespace="/shell")
                # Emit the response to the room corresponding to this agent.
                logger.debug(f"Emitting response to room: {agent_id}")
                ws.emit(
                    "on_agent_data",
                    {"agent_id": agent_id, "command_id": command_id, "data": data},
                    namespace="/shell",
                )

            else:
                logger.error("WebSocket client not connected.")

            # fialing as there's not command id entry on oneoffs... need to do a new entry?
            # Store the response in Redis, even if command_id is None.
            agent = Agent(agent_id)
            agent.store_response(command_id, data)

            return {"status": "received", "data": data}, 200

        except Exception as e:
            logger.error(f"Internal Server Error in POST endpoint: {str(e)}")
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
    serve(app, host=host, port=port, connection_limit=5000, threads=20)


def update_last_seen(agent_class):
    """
    Updates the last time an agent was seen.
    Triggers on GET request.
    Currently uses UTC datetime.
    """
    agent_class.data.agent.last_seen = str(get_utc_datetime())
    agent_class.unload_data()


# ------------------------------------------------------------------------------------
#   Main Execution
# ------------------------------------------------------------------------------------
if __name__ == "__main__":
    run_app("0.0.0.0", 5000)
