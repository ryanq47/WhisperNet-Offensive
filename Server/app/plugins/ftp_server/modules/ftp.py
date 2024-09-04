import os
import logging
from threading import Thread
from pathlib import Path
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
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
        self.root_directory = (Config().launch_path / "ftp").resolve()
        self.root_directory.mkdir(parents=True, exist_ok=True)

        self.authorizer = DummyAuthorizer()

        # Set up the handler
        self.handler = FTPHandler
        self.handler.authorizer = self.authorizer
        if banner:
            self.handler.banner = banner

        # Initialize FTP server with the handler
        self.server = PyFTPServer((self.ip, self.port), self.handler)
        self.server_thread = None

        

    def add_anonymous_user(self):
        try:
            ftp_logger.info("Adding anonymous FTP user with write-only access")
            self.authorizer.add_anonymous(str(self.root_directory), perm="w")
        except Exception as e:
            ftp_logger.error(f"Failed to add anonymous user: {e}")
            raise e

    def add_user(self, username: str, password: str):
        try:
            ftp_logger.info(f"Adding FTP user: {username}")
            self.authorizer.add_user(username, password, str(self.root_directory), perm="elradfmw")
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
                    info = "FTP Server",
                    timestamp = str(int(time.time()))
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
                    ftp_serv.delete()
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
