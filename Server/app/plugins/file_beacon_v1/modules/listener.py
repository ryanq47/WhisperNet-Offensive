import json
import signal
import socket
import struct
from multiprocessing import Process

from modules.client import BaseAgent
from modules.instances import Instance
from modules.listener import BaseListener
from modules.log import log

# from modules.redis_models import ActiveService
from modules.utils import api_response, generate_timestamp, generate_unique_id
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

    def __init__(self, port: int, host: str):
        # init super
        super().__init__()  # can give listener_id if there is one that needs to be respawned from redis data
        # make sure port is an int
        if not type(port) == int:
            port = int(port)

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
