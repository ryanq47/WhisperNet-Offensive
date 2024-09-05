from redis_om import get_redis_connection, Field, HashModel, JsonModel

redis = get_redis_connection(  # switch to config values
    host="localhost",
    port=6379,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)

# for global redis models

'''
# Define a model
class Product(HashModel):
    name: str = Field(index=True)
    price: float = Field(index=True)
    quantity: int

    class Meta:
        database = redis
'''

# client model 
class Client(HashModel):
    client_id: str = Field(index=True, primary_key=True)  # Indexed field
    type: str = Field(index=True)  # Indexed field
    checkin: int = Field(index=True)  # Indexed field

    class Meta:
        database = redis
        global_key_prefix = "client"  # Prefix for keys

# Create the index explicitly after defining the model
#Client.create_index()

class ActiveService(JsonModel):
    # need to determine a prefix + a diff between each instance?
    # service:somestuff:<service_uuid>?

    sid: str = Field(index=True, primary_key=True) # sid: server id
    port: int
    ip: str # ip/hostname, what it listends on
    info: str # info of waht the server is
    timestamp: str # time server is started?
    name: str # name of service

    class Meta:
        database = redis  # The Redis connection
        global_key_prefix = "service"
