import time

import redis
from modules.config import Config
from modules.log import log

logger = log(__name__)


# will need user/pass eventually
def redis_ping(max_attempts=10, interval=1):
    """
    Waits until Redis is available by attempting to ping it using redis-py.

    Gets values of host, and port, from the config file.
    host: redis.bind.ip
    port: redis.bind.port

    :param max_attempts: Maximum number of connection attempts
    :param interval: Seconds to wait between attempts
    :return: True if Redis is available, False otherwise
    """
    for attempt in range(1, max_attempts + 1):
        try:
            r = redis.Redis(
                host=Config().config.redis.bind.ip,
                port=Config().config.redis.bind.port,
                socket_connect_timeout=5,
            )
            if r.ping():
                logger.info("Redis connection established.")
                return True
        except redis.exceptions.ConnectionError as e:
            logger.debug(
                f"Attempt {attempt}/{max_attempts}: Redis not ready, waiting {interval} second(s)..."
            )
            time.sleep(interval)
    logger.error("Timeout waiting for Redis connection.")
    return False
