import json
import signal
import socket
import struct
from multiprocessing import Process

from modules.listener import BaseListener
from modules.log import log

# from modules.redis_models import ActiveService
from modules.utils import generate_timestamp, generate_unique_id
from plugins.file_beacon_v1.modules.vlmt import VLMT

logger = log(__name__)


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


# does this need its own listener .py?
class Listener(BaseListener):

    def __init__(self, port, host):
        # init super
        super().__init__()  # can give listener_id if there is one that needs to be respawned from redis data
        self.data.network.port = port
        self.data.network.address = host

        # auto call listener spawn? Should really only be called once
        # self.spawn()

    # Socket-based server/Listener
    def spawn(self):
        """
        Start a socket server for file-based beacon communication.
        """
        # register listener into redis, using register method in inhereted class
        self.register()

        # Spawn a new process for the server
        a = VLMT(self.data.network.port, self.data.network.address, self)
        process = Process(target=a.socket_server, daemon=False)
        process.start()
        logger.info(
            f"Spawned socket server for file-beacon-v1 on {self.data.network.address}:{self.data.network.port} with PID {process.pid}"
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
