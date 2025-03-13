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
from plugins.listener.http.http_server import run_app

import multiprocessing


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


class Listener(BaseListener):

    def __init__(self, host, name, port, listener_id=None):
        # init super
        super().__init__(listener_id=listener_id, port=port, host=host, name=name)

    # def spawn(self, port: int, host: str, name: str):
    def spawn(self):
        """
        Start the server as a child process and let the parent continue.
        """
        # make sure port is an int
        if not type(self.data.network.port) == int:
            self.data.network.port = int(self.data.network.port)

        # spawn the listener itself
        proc = self._spawn_agent_http_listener()
        if not proc:
            logger.warning("Failed to start listener!")
            return

        # giving it the PID for later loads if needed.
        self.data.listener.pid = proc.pid

        logger.info(
            f"Beacon HTTP listener spawned. Name={self.data.listener.name}, PID={proc.pid}, port={self.data.network.port}"
        )

        # Optionally store `proc` in self if you want to kill it later.
        self._process_handle = proc

    def _spawn_agent_http_listener(self):
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
