from redis_om import get_redis_connection
from redis_om import Migrator, HashModel
from modules.config import Config
from modules.log import log

logger = log(__name__)


# Connect to Redis
redis = get_redis_connection(  # switch to config values
    host=Config().config.redis.bind.ip,
    port=Config().config.redis.bind.port,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)
class RedisQueue:
    def __init__(self, client_id):
        """
            client_id: ID of client. This feild is used to create the entry for redis. 
                # note, should auto add if queue already exists
        """
        self.client_id = f"FormJQueue:{client_id}"

    def enqueue(self, item):
        """Add an item to the queue."""
        redis.lpush(self.client_id, item)

    def dequeue(self):
        """Remove and return the last item in the queue."""
        return redis.rpop(self.client_id)

    def size(self):
        """Get the current size of the queue."""
        return redis.llen(self.client_id)

    def peek(self):
        """Peek at the last item in the queue without removing it."""
        return redis.lindex(self.client_id, -1)

    def all_items(self):
        """Return all items in the queue."""
        return redis.lrange(self.client_id, 0, -1)
