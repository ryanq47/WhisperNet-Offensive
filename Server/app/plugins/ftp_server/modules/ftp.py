import os
import logging
from threading import Thread
from pathlib import Path
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, TLS_FTPHandler
from pyftpdlib.servers import FTPServer as PyFTPServer
from modules.config import Config
from modules.log import log
from modules.redis_models import ActiveService
import time

# Configure the logger for pyftpdlib
def configure_ftp_logging():
    ftp_logger = logging.getLogger('pyftpdlib')
    ftp_logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler('ftp_server.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    ftp_logger.addHandler(file_handler)
    ftp_logger.addHandler(stream_handler)

    return ftp_logger

ftp_logger = configure_ftp_logging()
logger = log(__name__)

class LeFTPServer:
    def __init__(self, ip, port, sid, banner=""):
        self.ip = ip
        self.port = port
        self.running = False

        self.sid = str(sid)

        # Set up the root directory
        self.root_directory = (Config().launch_path / ".." /"data" /"ftp").resolve()
        self.root_directory.mkdir(parents=True, exist_ok=True)

        self.authorizer = DummyAuthorizer()

        # Set up the handler
        if Config().config.server.ftp.tls.enabled:
            logger.info("FTP TLS is on")

            certfile = Config().launch_path / Config().config.server.ftp.tls.tls_crt_file
            keyfile = Config().launch_path / Config().config.server.ftp.tls.tls_key_file
            logger.info(f"Looking for keyfile at: {str(keyfile)}")
            logger.info(f"Looking for certfile at: {str(certfile)}")

            # Check if the certfile and keyfile exist
            if not certfile.exists():
                logger.warning(f"TLS certificate file {certfile} not found.")
                ftp_logger.warning(f"TLS certificate file {certfile} not found.")
                raise FileNotFoundError(f"TLS certificate file {certfile} not found.")
            
            if not keyfile.exists():
                logger.warning(f"TLS key file {keyfile} not found.")
                ftp_logger.warning(f"TLS key file {keyfile} not found.")
                raise FileNotFoundError(f"TLS key file {keyfile} not found.")

            # Set up the TLS handler
            self.handler = TLS_FTPHandler
            self.handler.certfile = str(certfile)  # Cast to string for compatibility
            self.handler.keyfile = str(keyfile)

        else:
            self.handler = FTPHandler

        self.handler.authorizer = self.authorizer
        if banner:
            self.handler.banner = banner

        # Initialize FTP server with the handler
        self.server = PyFTPServer((self.ip, self.port), self.handler)
        self.server_thread = None

        

    def add_anonymous_user(self):
        try:
            perms = Config().config.server.ftp.users.anonymous.permissions
            ftp_logger.info(f"Adding Anonymous FTP user with {perms} permissions")
            self.authorizer.add_anonymous(str(self.root_directory), perm=perms)
        except Exception as e:
            ftp_logger.error(f"Failed to add anonymous user: {e}")
            raise e

    def add_user(self, username: str, password: str):
        try:
            perms = Config().config.server.ftp.users.standard.permissions
            ftp_logger.info(f"Adding FTP user: {username} with {perms} permissions")
            self.authorizer.add_user(username, password, str(self.root_directory), perm=perms)
        except Exception as e:
            ftp_logger.error(f"Failed to add user {username}: {e}")
            raise e

    def start_server(self):
        if not self.running:
            try:
                ftp_logger.info(f"Starting FTP server on {self.ip}:{self.port}")
                self.server_thread = Thread(target=self.server.serve_forever, daemon=True)
                self.server_thread.start()
                self.running = True
                
                # add ftp serv to redis
                logger.debug("Adding service key to redis")
                ftp_serv = ActiveService(
                    sid = self.sid,
                    port = self.port,
                    ip = self.ip,
                    info = "FTP Server DESC Placeholder", # can add to self.init if needed
                    timestamp = str(int(time.time())),
                    name="FTP Server"
                )

                ftp_serv.save()   
            except Exception as e:
                ftp_logger.error(f"Failed to start server: {e}")
                raise e

    def stop_server(self):
        if self.running:
            try:
                ftp_logger.info(f"Stopping FTP server on {self.ip}:{self.port}")
                self.server.close_all()
                self.running = False
                
                ftp_serv = ActiveService.get(self.sid)                
                if ftp_serv:
                    ftp_serv.delete(self.sid)
                    logger.info("Service key removed from Redis using ORM")
                else:
                    logger.warning("No matching service key found in Redis to remove")
                    


            except Exception as e:
                ftp_logger.error(f"Failed to stop server: {e}")
                raise e

if __name__ == "__main__":
    ftp_server = LeFTPServer('0.0.0.0', 21)
    ftp_server.add_anonymous_user()
    ftp_server.add_user('dedicated_user', 'password')
    ftp_server.start_server()
