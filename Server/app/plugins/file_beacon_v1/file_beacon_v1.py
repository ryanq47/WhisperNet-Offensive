import json
import logging
import signal
import socket
import struct
from multiprocessing import Process

from modules.redis_models import ActiveService
from modules.utils import generate_timestamp, generate_unique_id
from plugins.file_beacon_v1.modules.vlmt import VLMT

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

"""
Plan: 
 - Class:
     - Maybe the socket stuff?
     - Would also need a client class, that handles furtehr processing. replace handle_client.

    On cilent class load, inheret the Client base class, and it will load data from redis if client exists



"""


class Info:
    name = "file-beacon-v1"
    author = "ryanq.47"


# Socket-based server/Listener
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
    a = VLMT(port, host, nickname)
    process = Process(target=a.socket_server, daemon=False)
    process.start()
    logger.info(
        f"Spawned socket server for file-beacon-v1 on {host}:{port} with PID {process.pid}"
    )
    return process


# # class this?
# def handle_client(client_socket):
#     """
#     Handle incoming client requests.
#     """
#     try:
#         # get message
#         # Get length of message (8 bytes for the length prefix)
#         length_prefix = client_socket.recv(8)
#         if not length_prefix:
#             logger.error("Failed to receive the length prefix.")
#             return None

#         # Unpack the length prefix to get the message length
#         message_length = struct.unpack("!Q", length_prefix)[0]
#         logger.info(f"Message length received: {message_length}")

#         # Get the rest of the message
#         contents = b""
#         while len(contents) < message_length:
#             chunk = client_socket.recv(
#                 min(4096, message_length - len(contents))
#             )  # Read up to the remaining bytes
#             if not chunk:  # Connection closed prematurely
#                 logger.error("Connection closed before the full message was received.")
#                 return None
#             logger.info(f"Received chunk of size {len(chunk)}: {chunk}")

#             contents += chunk

#         logger.info(f"Full message of size {message_length} recieved")

#         print(contents)

#         # Decode the full message and return
#         client_socket.sendall("ok".encode("utf-8"))
#         return contents.decode("utf-8")

#         # # Receive data
#         # data = client_socket.recv(4096).decode("utf-8")
#         # logger.info(f"Received data: {data}")

#         # # Parse incoming JSON/FormJ data
#         # request = json.loads(data)

#         # # Example of processing a request
#         # response = {
#         #     "status": "ok",
#         #     "action": request.get("action", "unknown"),
#         #     "message": "Processed successfully",
#         # }

#         # # Send response back to client
#         # client_socket.sendall(json.dumps(response).encode("utf-8"))
#     except Exception as e:
#         logger.error(f"Error handling client request: {e}")
#         error_response = json.dumps({"status": "error", "message": str(e)})
#         client_socket.sendall(error_response.encode("utf-8"))
#     finally:
#         # Close client connection
#         client_socket.close()
