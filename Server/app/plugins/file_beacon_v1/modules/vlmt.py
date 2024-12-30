import signal
import socket
import struct

from modules.log import log
from modules.redis_models import Agent

logger = log(__name__)


class VLMT:
    def __init__(self, port, host, nickname):
        self.socket_timeout = 60
        self.server_socket = None
        self.port = port
        self.host = host
        self.nickname = nickname

    def socket_server(self):
        """
        Socket server implementation with graceful shutdown.
        Call from a thread/process to be non-blocking.
        """

        def shutdown_handler(signum, frame):
            """Gracefully shut down the server."""
            if self.server_socket:
                logger.info(
                    f"Shutting down server on {self.host}:{self.port} (nickname: {self.nickname})"
                )
                self.server_socket.close()
            exit(0)

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        try:
            # Create and bind the socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # allow socket reuse
            logger.warning(f"Socket reuse enabled for vlmt.py, on port {self.port}")
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)  # Listen for up to 5 connections
            logger.info(
                f"Socket server started on {self.host}:{self.port}, nickname: {self.nickname}"
            )

            while True:
                # Accept a new connection
                client_socket, client_address = self.server_socket.accept()
                logger.info(f"Connection received from {client_address}")

                # Handle client request
                self.handle_client(client_socket)

        except Exception as e:
            logger.error(f"Error in socket server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    # CLEANUP
    def handle_client(self, client_socket):
        """
        Handle incoming client requests.
        """
        try:
            client_socket.settimeout(5)  # Set timeout in seconds

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
                    logger.error(
                        "Connection closed before the full message was received."
                    )
                    return None
                logger.info(f"Received chunk of size {len(chunk)}: {chunk}")

                contents += chunk

            logger.info(f"Full message of size {message_length} recieved")

            # print(contents)
            logger.debug(contents)

            c = Client(id="SOMEID")
            # Spawn client class, and let it do its thing
            # queue, dequue, register, etc?

            # send appropriate message back
            # client_socket.sendall("ok".encode("utf-8"))

            command = c.dequeue()
            # some processing...
            # with dequeue:
            client_socket.sendall(command.encode("utf-8"))

        except socket.timeout:
            logger.error(f"Socket timed out after 5 seconds while receiving data.")
            return None

        except Exception as e:
            logger.error(e)
            raise e

        finally:
            client_socket.close()
