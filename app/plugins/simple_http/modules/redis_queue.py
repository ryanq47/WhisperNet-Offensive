from redis_om import get_redis_connection
from redis_om import Migrator, HashModel
from modules.config import Config
from modules.log import log
import re

logger = log(__name__)

# Connect to Redis
redis = get_redis_connection(  # switch to config values
    host=Config().config.redis.bind.ip,
    port=Config().config.redis.bind.port,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)

def sanitize_input(value):
    """
    Sanitize input to allow only alphanumeric characters, underscores, and hyphens.
    """
    return re.match(r'^[\w-]+$', value) is not None

class RedisQueue:
    def __init__(self, client_id):
        """
        Initialize the RedisQueue with a client_id, ensuring it's sanitized to prevent injection.
        """
        # check if the stirng contains something that's not alphanum and -. 
        # I've seen varied reports that redis can/can't be injected, this is just a safeguard.
        if not sanitize_input(client_id):
            raise ValueError(f"Invalid client_id format: {client_id}")

        # If valid, create the Redis key for this client's queue
        self.client_id = f"FormJQueue:{client_id}"

    def enqueue(self, item):
        """Add an item to the queue."""
        try:
            redis.lpush(self.client_id, item)

        except Exception as e:
            logger.error(e)
            raise e

    def dequeue(self):
        """Remove and return the last item in the queue."""
        try:
            return redis.rpop(self.client_id)
        except Exception as e:
            logger.error(e)
            raise e

    def size(self):
        """Get the current size of the queue."""

        try:
            return redis.llen(self.client_id)
        except Exception as e:
            logger.error(e)
            raise e

    def peek(self):
        """Peek at the last item in the queue without removing it."""
        try:
            return redis.lindex(self.client_id, -1)
        except Exception as e:
            logger.error(e)
            raise e

    def all_items(self):
        """Return all items in the queue."""
        try:
            return redis.lrange(self.client_id, 0, -1)
        except Exception as e:
            logger.error(e)
            raise e