# Whispernet Redis Setup Guide

Whispernet requires Redis for fast in-memory operations, along with RedisJSON for handling JSON objects. More specifically, redis-stack-server. 


## Todo:
 - [ ] Handle start/stop of docker container?/better startup docker chekcing if containre is there etc

 - [ ] Get endpoint: Figure out the reqis queue stuff, one queue per client, based on client uuid


# idea: 
# use this to store rid's, for which one to pop next.
 ```
 from redis_om import get_redis_connection
from redis_om import Migrator, HashModel

# Connect to Redis
redis = get_redis_connection()

class RedisQueue:
    def __init__(self, name):
        self.name = name

    def enqueue(self, item):
        """Add an item to the queue."""
        redis.lpush(self.name, item)

    def dequeue(self):
        """Remove and return the last item in the queue."""
        return redis.rpop(self.name)

    def size(self):
        """Get the current size of the queue."""
        return redis.llen(self.name)

    def peek(self):
        """Peek at the last item in the queue without removing it."""
        return redis.lindex(self.name, -1)

    def all_items(self):
        """Return all items in the queue."""
        return redis.lrange(self.name, 0, -1)

 
 
 
 ```