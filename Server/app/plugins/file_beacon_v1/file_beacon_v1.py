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


class Info:
    name = "file-beacon-v1"
    author = "ryanq.47"


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
    a = VLMT(port, host, nickname)
    process = Process(target=a.socket_server, daemon=False)
    process.start()
    logger.info(
        f"Spawned socket server for file-beacon-v1 on {host}:{port} with PID {process.pid}"
    )
    return process


# def socket_server(port, host, nickname):
#     """
#     Socket server implementation with graceful shutdown.
#     """
#     server_socket = None

#     def shutdown_handler(signum, frame):
#         """Gracefully shut down the server."""
#         nonlocal server_socket
#         if server_socket:
#             logger.info(f"Shutting down server on {host}:{port} (nickname: {nickname})")
#             server_socket.close()
#         exit(0)

#     # Register signal handlers for graceful shutdown
#     signal.signal(signal.SIGINT, shutdown_handler)
#     signal.signal(signal.SIGTERM, shutdown_handler)

#     try:
#         # Create and bind socket
#         server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         server_socket.bind((host, port))
#         server_socket.listen(5)  # Listen for up to 5 connections
#         logger.info(f"Socket server started on {host}:{port}, nickname: {nickname}")

#         while True:
#             # Accept a new connection
#             client_socket, client_address = server_socket.accept()
#             logger.info(f"Connection received from {client_address}")

#             # Handle client request
#             handle_client(client_socket)
#     except Exception as e:
#         logger.error(f"Error in socket server: {e}")
#     finally:
#         if server_socket:
#             server_socket.close()


def handle_client(client_socket):
    """
    Handle incoming client requests.
    """
    try:
        # get message
        # Get length of message (8 bytes for the length prefix)
        length_prefix = client_socket.recv(8)
        if not length_prefix:
            logger.error("Failed to receive the length prefix.")
            return None

        # Unpack the length prefix to get the message length
        message_length = struct.unpack("!Q", length_prefix)[0]
        logger.info(f"Message length received: {message_length}")

        # Get the rest of the message
        contents = b""
        while len(contents) < message_length:
            chunk = client_socket.recv(
                min(4096, message_length - len(contents))
            )  # Read up to the remaining bytes
            if not chunk:  # Connection closed prematurely
                logger.error("Connection closed before the full message was received.")
                return None
            logger.info(f"Received chunk of size {len(chunk)}: {chunk}")

            contents += chunk

        logger.info(f"Full message of size {message_length} recieved")

        print(contents)

        # Decode the full message and return
        client_socket.sendall("ok".encode("utf-8"))
        return contents.decode("utf-8")

        # # Receive data
        # data = client_socket.recv(4096).decode("utf-8")
        # logger.info(f"Received data: {data}")

        # # Parse incoming JSON/FormJ data
        # request = json.loads(data)

        # # Example of processing a request
        # response = {
        #     "status": "ok",
        #     "action": request.get("action", "unknown"),
        #     "message": "Processed successfully",
        # }

        # # Send response back to client
        # client_socket.sendall(json.dumps(response).encode("utf-8"))
    except Exception as e:
        logger.error(f"Error handling client request: {e}")
        error_response = json.dumps({"status": "error", "message": str(e)})
        client_socket.sendall(error_response.encode("utf-8"))
    finally:
        # Close client connection
        client_socket.close()
