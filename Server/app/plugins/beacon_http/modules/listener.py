import json
import signal
import socket
import struct
from multiprocessing import Process
import os, signal

from modules.agent import BaseAgent
from modules.instances import Instance
from modules.listener import BaseListener
from modules.log import log
from plugins.beacon_http.modules.http_server import run_app

import multiprocessing

# from modules.redis_models import ActiveService
from modules.utils import api_response, generate_timestamp, generate_unique_id


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

    def __init__(self, listener_id=None):
        # init super
        super().__init__(listener_id)

    def spawn(
        self,
        port: int,
        host: str,
    ):
        """
        Start the server as a child process and let the parent continue.
        """
        # make sure port is an int
        if not type(port) == int:
            port = int(port)

        self.data.network.port = port
        self.data.network.address = host

        proc = self._spawn_beacon_http_listener()
        if not proc:
            logger.warning("Failed to start listener!")
            return

        # giving it the PID for later loads if needed.
        self.data.listener.pid = proc.pid

        # DO NOT JOIN here or you'll block the parent process.
        logger.info(
            f"Beacon HTTP listener spawned. PID={proc.pid}, port={self.data.network.port}"
        )

        self.register()  # to store in redis

        # Optionally store `proc` in self if you want to kill it later.
        self._process_handle = proc

    def _spawn_beacon_http_listener(self):
        """
        Launch the mini Flask RESTX server in its own process.
        """
        proc = multiprocessing.Process(
            target=run_app,
            args=(self.data.network.address, self.data.network.port),
        )
        proc.start()
        return proc

    def kill(self):
        """
        Kills the listener

        """

        try:
            os.kill(self._data.listener.pid, signal.SIGTERM)
            logger.debug(f"Sent SIGTERM to process {self.data.listener.pid}")
            self.unregister()
        except ProcessLookupError:
            print(f"No such process {self.data.listener.pid}")
        except PermissionError:
            print(f"No permission to kill {self.data.listener.pid}")
