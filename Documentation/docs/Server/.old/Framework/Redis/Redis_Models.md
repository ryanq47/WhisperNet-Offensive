# Redis Models

`redis_om` is the ORM used to interact with redis. Below are the models available to the entire program.

Each plugin can have its own Redis models definition file, keeping data schemas isolated and easy to manage, ensuring flexibility and reducing conflicts across plugins.

## Importing these modules

`from modules.redis_models import ...`

## Using these models

To use these models, follow the redis-om docs: https://redis.io/docs/latest/integrate/redisom-for-python/

If you don't want to dig through those, a basic example to save to the redis db is as such:

```py
#import the class
from modules.redis_models import SomeModel

#Init the class
c = SomeModel(
        name=container_name,
        # any other options defined in the model
    )

# Call the save method, which saves it to the DB
c.save()
```

## [X] Agent Model

The agent model is used for registering agents/tracking that them exist

`agent_id`: The unique field used to distinguish Agents. Needs to be *UNIQUE* or you may run into collision issues.

```py
class Agent(HashModel):
    agent_id: str = Field(index=True, primary_key=True)  # Indexed field

    class Meta:
        model_key_prefix = "client"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys
```

### Example Usage

```py
redis_agent_class = Agent(agent_id="SOMEID")
redis_agent_class.save()
```

## [X] AgentData Model

The `AgentData` model is used to store data for agents. 

`agent_id`: The unique field used to distinguish Agents. Should be the same as the one used in the Agent Model if the Agents are the same.

`json_blob`: The json string with data from the class. If using `BaseAgent`, the `unload_data` function does this.

```py
class AgentData(HashModel):
    agent_id: str = Field(index=True, primary_key=True)  # Indexed field
    json_blob: str

    class Meta:
        model_key_prefix = "agent:data"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys
```

### Example Usage

```py
mydict = {"key":"value"}
json_blob = json.dumps(mydict)
redis_agent_class = AgentData(agent_id="SOMEID", json_blob=json_blob)
redis_agent_class.save()
```

## AgentCommand Model

The `AgentCommand` model is used to store commands for the agents. 

`command_id`: The command ID (UUID). This is generated in code when `BaseAgent.enqueue_command()` is called

`agent_id`: The agent ID (UUID). 

`command`: The actual command in which to run on the agent. 

`response`: A placeholder/field for the response from running the command. Initially empty, is updated upon completion of the command

`timestamp`: A timestamp for tracking the time *when the command was enqueued*. NOT when it was run. In ISO format, ex: `2023-11-28T17:45:03.123456+00:00`



#### Key Format: `whispernet:agent:command:328bdc4c-b85f-4ca0-8293-b8be36438d61`



Note: The order at which these commands are retireved are dictedated by a per-client command queue. 

```py
class AgentCommand(HashModel):
    command_id: str = Field(index=True, primary_key=True)  # Indexed field
    agent_id: str  # For which agent this command is
    command: str
    response: str
    timestamp: str = Field(
        index=True, default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    class Meta:
        model_key_prefix = "agent:command"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys
```



## [X] Listener Model

The Listener model is used to store data for listeners that exist.

`listener_id`: The unique field used to distinguish Listeners. I'd reccommend a UUID of some sorts

`name`: The name of the listener

```py
class Listener(HashModel):
    listener_id: str = Field(index=True, primary_key=True)  # Indexed field
    name: str = Field()

    class Meta:
        model_key_prefix = "listener"
        database = redis
        global_key_prefix = "whispernet"  # Prefix for keys
```

Example Usage:

```
redis_listener_class = Listener(listener_id="SOMEID")
redis_listener_class.save()
```

THe client model is meant to be a standard way to store light details on a client, such as checkin times, and type. 

Basically, when a client checks in, either a key is created, or updated, based on it's ID with the follwoing information:

```
class Agent(HashModel):
    client_id: str = Field(index=True, primary_key=True)  # ID of the client (UUID4)
    type: str = Field(index=True)                         # Client type, such as `simple_http`. 
    checkin: int = Field(index=True)                      # last checkin time, in unix time

    class Meta:
        database = redis
        global_key_prefix = "client"                      # Prefix for keys
```

```
127.0.0.1:6379> hgetall client:modules.redis_models.Client:d94670d6-bc49-4ed7-8f26-fd8470e77fa2
1) "pk"
2) "01J66NVYW5F1RKEJ5P164XHXWP"
3) "client_id"
4) "d94670d6-bc49-4ed7-8f26-fd8470e77fa2"
5) "type"
6) "simple-http"
7) "checkin"
8) "1724653632"
```

Together, all these keys make up the contents of the `/clients` endpoint, which contain all the clients:

```
{
  "data": {
    "client:modules.redis_models.Client:02637f18-14f4-4c3d-a4cf-ee95e6a33037": {
      "checkin": "1724653632",
      "client_id": "02637f18-14f4-4c3d-a4cf-ee95e6a33037",
      "pk": "01J66NVYZQDAA9R671YBCD5PSX",
      "type": "simple-http"
    },
    "client:modules.redis_models.Client:0864c139-134f-4fa0-b68a-61ffb9b8591e": {
      "checkin": "1724653631",
      "client_id": "0864c139-134f-4fa0-b68a-61ffb9b8591e",
      "pk": "01J66NVYDVCN203BEVZJQ67FGJ",
      "type": "simple-http"
    },
  "message": "",
  "rid": "294ed3b7-2b6a-4f2c-b673-24c5a3361988",
  "status": 200,
  "timestamp": 1724653653
}

```

## DEPRECATED Client model

## Active Service Model

The active service model is used to store the current active services on the server. It's primarily used by the stats plugin to allow the WebClient to view the current active Services. This is different than Plugin/Container models, as this only holds data of the *service*, not the method it's being run with. 

TLDR: Implementation agnostic service display

```
class ActiveService(JsonModel):
    # need to determine a prefix + a diff between each instance?
    # service:somestuff:<service_uuid>?

    sid: str = Field(index=True, primary_key=True)  # sid: service id, UUID4
    port: int                                       # Port of service
    ip: str                                         # ip/hostname, what it listends on
    info: str                                       # info of waht the server is
    timestamp: str                                  # time server is started
    name: str                                       # name of service

    class Meta:
        database = redis                            # The Redis connection
        global_key_prefix = "service"               # Prefix of key
```

## Plugin Model

The plugin model is used to store the currently loaded plugins on the server. It's also used primarily by the stats plugin to allow the WebClient to interact with/view/control the current plugins.

```
class Plugin(JsonModel):
    name: str = Field(index=True, primary_key=True) # name of plugin, make primary key so it doesnt repeat


    # optional fields for if the service has a start/stop componenet
    start: str = Field(default="")                  # start field, holds endpoint to start service, ex /ftp/start
    stop: str = Field(default="")                   # stop field, same as above but for stopping  
    info: str = Field(default="No info provided")   # Info field for the plugin

    class Meta:
        database = redis                            # The Redis connection
        global_key_prefix = "plugin"                # Prefix of key
```

## Container Model

The Container model is used for tracking all the containers that are up. 

```
class Plugin(JsonModel):
    name: str = Field(index=True, primary_key=True) # name of plugin, make primary key so it doesnt repeat


    # optional fields for if the service has a start/stop componenet
    start: str = Field(default="")                  # start field, holds endpoint to start service, ex /ftp/start
    stop: str = Field(default="")                   # stop field, same as above but for stopping  
    info: str = Field(default="No info provided")   # Info field for the plugin

    class Meta:
        database = redis                            # The Redis connection
        global_key_prefix = "plugin"                # Prefix of key
```