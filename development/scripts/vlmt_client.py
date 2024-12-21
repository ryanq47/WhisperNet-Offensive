import socket
import struct


def send_vlmt_message(server_host, server_port, message):
    try:
        # Connect to the server
        with socket.create_connection((server_host, server_port)) as sock:
            # Prepare the message
            payload = message.encode()  # Convert message to bytes
            length_prefix = struct.pack(
                "!Q", len(payload)
            )  # 8-byte length prefix in network byte order

            # Send length prefix followed by the payload
            sock.sendall(length_prefix + payload)
            print(f"Sent message: {message}")

            # Optionally receive acknowledgment from server (if needed)
            response = sock.recv(1024)  # Adjust buffer size as needed
            print(f"Received from server: {response.decode()}")

    except Exception as e:
        print(f"Error: {e}")


# Example usage
if __name__ == "__main__":
    SERVER_HOST = "127.0.0.1"  # Replace with server IP
    SERVER_PORT = 9006  # Replace with server port
    MESSAGE = "Hello, this is VLMT client!"

    send_vlmt_message(SERVER_HOST, SERVER_PORT, MESSAGE)
