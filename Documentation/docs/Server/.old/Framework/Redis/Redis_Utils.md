# Redis Utils

The redis utils model is a set of utilites that are handy for interacting with redis

### Function: `redis_ping`

The `redis_ping` function verifies the availability of a Redis server by attempting to connect and send a `PING` command using the `redis-py` library. It retrieves the Redis host and port from a configuration file (`Config().config.redis.bind.ip` and `Config().config.redis.bind.port`) and tries to establish a connection up to `max_attempts` times, waiting `interval` seconds between each try.

If a successful `PING` response is received within the allotted attempts, the function logs that the Redis connection is established and returns `True`, allowing the application to proceed. If all attempts fail, it logs an error indicating a timeout and returns `False`, enabling the application to handle the unavailability of Redis appropriately, such as by retrying later or exiting gracefully.

#### Example Usage:


```
from modules.redis_utils import redis_ping

if redis_ping(max_attempts=10, interval=1):
    logger.info("Redis is available. Starting application...")
    # Proceed with application initialization
else:
    logger.error("Failed to connect to Redis. Exiting application.")
    sys.exit(1)
```