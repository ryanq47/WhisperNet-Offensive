<<<<<<< Updated upstream
"""
A file-based beacon.

Comms:
 - FormJ


"""

import json
import time
import traceback

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from modules.audit import Audit
from modules.config import Config
from modules.form_j import FormJ
from modules.instances import Instance
from modules.log import log
from modules.redis_models import Client
from modules.utils import api_response
from plugins.simple_http.modules.redis_models import FormJModel
from plugins.simple_http.modules.redis_queue import RedisQueue
from redis.commands.json.path import Path
from redis_om import HashModel, NotFoundError, get_redis_connection

logger = log(__name__)
# app = Instance().app

redis = get_redis_connection(  # switch to config values
    host=Config().config.redis.bind.ip,
    port=Config().config.redis.bind.port,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)
=======
import json
import logging
import socket
from multiprocessing import Process

from modules.redis_models import ActiveService
from modules.utils import generate_timestamp, generate_unique_id

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
>>>>>>> Stashed changes


class Info:
    name = "file-beacon-v1"
    author = "ryanq.47"


<<<<<<< Updated upstream
# Optional route example
@app.route(f"/balls", methods=["GET"])
def myfunctionfromhell():
    return jsonify({"somekey": "somevalue"})


# if __name__ == "__main__":


## Spawn function to be called
def spawn(port, host, nickname=None):
    try:
        logger.debug("Starting file-beacon-v1")
        app.run(debug=True, port=8082, host="0.0.0.0")

    except Exception as e:
        print(e)
=======
# Socket-based server
def spawn(port=8082, host="0.0.0.0", nickname=None):
    """
    Start a socket server for file-based beacon communication.
    """
    # Save listener details
    r_listener = ActiveService(
        sid=generate_unique_id(),
        port=port,
        ip=host,
        info="file_beacon_v1 service/listener",
        timestamp=str(generate_timestamp()),
        name="file_beacon_v1",
    )
    r_listener.save()

    # Spawn a new process for the server
    process = Process(target=socket_server, args=(port, host, nickname), daemon=True)
    process.start()
    logger.info(
        f"Spawned socket server for file-beacon-v1 on {host}:{port} with PID {process.pid}"
    )
    return process


def socket_server(port, host, nickname):
    """
    Socket server implementation.
    """
    try:
        # Create and bind socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5)  # Listen for up to 5 connections
        logger.info(f"Socket server started on {host}:{port}, nickname: {nickname}")

        while True:
            # Accept a new connection
            client_socket, client_address = server_socket.accept()
            logger.info(f"Connection received from {client_address}")

            # Handle client request
            handle_client(client_socket)
    except Exception as e:
        logger.error(f"Error in socket server: {e}")


def handle_client(client_socket):
    """
    Handle incoming client requests.
    """
    try:
        # Receive data
        data = client_socket.recv(4096).decode("utf-8")
        logger.info(f"Received data: {data}")

        # Parse incoming JSON/FormJ data
        request = json.loads(data)

        # Example of processing a request
        response = {
            "status": "ok",
            "action": request.get("action", "unknown"),
            "message": "Processed successfully",
        }

        # Send response back to client
        client_socket.sendall(json.dumps(response).encode("utf-8"))
    except Exception as e:
        logger.error(f"Error handling client request: {e}")
        error_response = json.dumps({"status": "error", "message": str(e)})
        client_socket.sendall(error_response.encode("utf-8"))
    finally:
        # Close client connection
        client_socket.close()
>>>>>>> Stashed changes
