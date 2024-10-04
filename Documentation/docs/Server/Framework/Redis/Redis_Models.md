# Redis Models

`redis_om` is the ORM used to interact with redis. Below are the models available to the entire program.

Each plugin can have its own Redis models definition file, keeping data schemas isolated and easy to manage, ensuring flexibility and reducing conflicts across plugins.

## Importing these modules

`from modules.redis_models import ...`

## Using these models

To use these models, follow the redis-om docs: https://redis.io/docs/latest/integrate/redisom-for-python/

If you don't want to dig through those, a basic example to save to the redis db is as such:

```
#Init the class
c = SomeModel(
        name=container_name,
        # any other options defined in the model
    )

# Call the save method, which saves it to the DB
c.save()
```


## Client model
THe client model is meant to be a standard way to store light details on a client, such as checkin times, and type. 
Basically, when a client checks in, either a key is created, or updated, based on it's ID with the follwoing information:

```
class Client(HashModel):
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