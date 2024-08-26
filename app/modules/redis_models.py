from redis_om import get_redis_connection, Field, HashModel

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
