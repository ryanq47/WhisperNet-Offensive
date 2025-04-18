from modules.config import Config
from redis_om import Field, HashModel, JsonModel, get_redis_connection
from modules.utils import get_utc_datetime

# fix this
redis = get_redis_connection(  # switch to config values
    host="localhost",
    port=6379,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)

## Problem: Config is not loaded by the time this is first called.
# redis = get_redis_connection(  # switch to config values
#     host=Config().config.redis.bind.ip,
#     port=Config().config.redis.bind.port,
#     decode_responses=True,  # Ensures that strings are not returned as bytes
# )

# for global redis models

"""
# Define a model
class Product(HashModel):
    name: str = Field(index=True)
    price: float = Field(index=True)
    quantity: int

    class Meta:
        database = redis
"""


# client model
class Agent(HashModel):  # swich to JsonModel?
    agent_id: str = Field(index=True, primary_key=True)  # Indexed field
    # type: str = Field(index=True)  # Indexed field
    # checkin: int = Field(index=True)  # Indexed field

    class Meta:
        model_key_prefix = "agent"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys


# client model
class AgentData(HashModel):
    agent_id: str = Field(index=True, primary_key=True)  # Indexed field
    json_blob: str

    class Meta:
        model_key_prefix = "agent:data"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys


class AgentCommand(HashModel):
    command_id: str = Field(index=True, primary_key=True)  # Indexed field
    agent_id: str  # For which agent this command is
    command: str
    response: str
    timestamp: str = Field(index=True, default_factory=lambda: str(get_utc_datetime()))

    class Meta:
        model_key_prefix = "agent:command"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys


# Create the index explicitly after defining the model
# Client.create_index()

# question - store data in one model, or just use one for reg, and one for
# data?
# For now, split. Need to still figure out how to get json directly into redis.


class Listener(HashModel):
    listener_id: str = Field(index=True, primary_key=True)  # Indexed field
    name: str = Field()
    # type: str = Field(index=True)  # Indexed field

    class Meta:
        # swap model_key and global_key... yay
        model_key_prefix = "listener"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys


class ListenerData(HashModel):
    listener_id: str = Field(index=True, primary_key=True)  # Indexed field
    json_blob: str

    class Meta:
        model_key_prefix = "listener:data"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for k


class ActiveService(JsonModel):
    # need to determine a prefix + a diff between each instance?
    # service:somestuff:<service_uuid>?

    sid: str = Field(index=True, primary_key=True)  # sid: server id
    port: int
    ip: str  # ip/hostname, what it listends on
    info: str  # info of waht the server is
    timestamp: str  # time server is started?
    name: str  # name of service

    class Meta:
        model_key_prefix = "service"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys


class Plugin(JsonModel):
    name: str = Field(
        index=True, primary_key=True
    )  # name of plugin, make primary key so it doesnt repeat

    # optional fields for if the service has a start/stop componenet
    start: str = Field(
        default=""
    )  # start field, holds endpoint to start service, ex /ftp/start
    stop: str = Field(default="")  # stop field, same as above but for stopping
    info: str = Field(default="No info provided")

    class Meta:
        model_key_prefix = "plugin"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys


class Container(JsonModel):
    name: str = Field(
        index=True, primary_key=True
    )  # name of Container, make primary key so it doesnt repeat
    # options: str # options field for options. not great but it works

    image: str = Field(default="Container missing an Image name")  # Docker image name
    volumes: str = Field(default="Container has no Volumes")  # Volmes if any
    hostname: str = Field(default="Container has no hostname")  # hostname of container
    ports: str = Field(
        default="Container has no exposed ports"
    )  # exposed ports in container

    # optional fields for if the service has a start/stop componenet
    # start: str = Field(default="") # start field, holds endpoint to start service, ex /ftp/start
    # stop: str = Field(default="") # stop field, same as above but for stopping

    # info: str = Field(default="No info provided")
    # ip: str # ip/hostname, what it listends on if it has a service on it
    # port: int

    class Meta:
        model_key_prefix = "container"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys
