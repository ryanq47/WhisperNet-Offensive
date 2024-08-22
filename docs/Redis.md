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


 ## Queue/command logic

2 items:

 - Queue: Used to hold the RID of the requests. does NOT hold the request itself
    WHen a command is requested, pop the numb from the queue, and do a search for the correspoding RID
    Ex: [1,2,3,4,5,6,7,8], etc


- RID keys:
    RID keys are just formJ entries labeled with the RID as their key. In this case, they hold a formJ command. On request, that search finds the correct key (if exists), and reutrns the data



Left off doing above. Was working on test for the command queue.
     - Ran into another hiccup: Docker container not responding for redis. would just hang/not connect. 
    - once that's fixed go continue testing/setting up command/client_id endpoint.

