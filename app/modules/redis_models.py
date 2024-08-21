from redis_om import get_redis_connection, HashModel, Field

redis = get_redis_connection(  # switch to config values
    host="localhost",
    port=6379,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)


# Define a model
class Product(HashModel):
    name: str = Field(index=True)
    price: float = Field(index=True)
    quantity: int

    class Meta:
        database = redis
