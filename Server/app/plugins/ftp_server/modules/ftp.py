import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer as PyFTPServer
from pyftpdlib.filesystems import AbstractedFS
import logging
from threading import Thread
from pathlib import Path
from modules.config import Config
from modules.log import log

# Configure the logger for pyftpdlib
ftp_logger = logging.getLogger('pyftpdlib')
ftp_logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('ftp_server.log')
file_handler.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

ftp_logger.addHandler(file_handler)
ftp_logger.addHandler(stream_handler)

# Main Logger
logger = log(__name__)


class LeFTPServer:
    def __init__(self, ip, port, banner=""):
        self.ip = ip
        self.port = port
        # change to serv root
        self.root_directory = (Config().launch_path / "ftp").resolve()  # Ensure the root directory is absolute
        if not self.root_directory.exists():
            ftp_logger.info(f"Creating FTP root directory at {self.root_directory}")
            self.root_directory.mkdir(parents=True, exist_ok=True)  # Create the directory

        
        # Set up the authorizer
        self.authorizer = DummyAuthorizer()

        # Set up the handler
        self.handler = FTPHandler
        self.handler.authorizer = self.authorizer

        if banner != "":
            self.handler.banner = banner 

        # Initialize FTP server with the handler
        self.server = PyFTPServer((self.ip, self.port), self.handler)
        self.running = False

    def add_anonymous_user(self):
        try:
            ftp_logger.info("Adding anonymous FTP user with write-only access")

            # Set up anonymous access with write-only permissions
            self.authorizer.add_anonymous(str(self.root_directory), perm="w")

        except Exception as e:
            ftp_logger.error(e)
            raise e

    def add_user(self, username: str, password: str):
        try:
            ftp_logger.info(f"Adding FTP user: {username}")

            # Add the user with full access permissions
            self.authorizer.add_user(username, password, str(self.root_directory), perm="elradfmw")
        
        except Exception as e:
            ftp_logger.error(e)
            raise e

    def start_server(self):
        try:
            if not self.running:
                ftp_logger.info(f"Starting FTP server on {self.ip}:{self.port}")
                self.running = True
                server_thread = Thread(target=self.server.serve_forever)
                server_thread.daemon = True
                server_thread.start()

        except Exception as e:
            ftp_logger.error(e)
            raise e

    def stop_server(self):
        try:
            if self.running:
                ftp_logger.info(f"Stopping FTP server on {self.ip}:{self.port}")
                self.server.close_all()
                self.running = False

        except Exception as e:
            ftp_logger.error(e)
            raise e
# Example usage:
if __name__ == "__main__":
    ftp_server = LeFTPServer('0.0.0.0', 21)  # Use appropriate IP and port
    ftp_server.add_anonymous_user()  # Add anonymous user with write-only access
    ftp_server.add_user('dedicated_user', 'password')  # Add a dedicated user with full access
    ftp_server.start_server()
