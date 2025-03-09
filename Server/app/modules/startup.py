"""

Various startup items

"""

from modules.docker_handler import (
    container_exists,
    pull_and_run_container,
    start_container,
    wait_for_container,
)
from modules.log import log
from modules.listener import ListenerStore
from plugins.listener.http.listener import Listener as HTTPListener

logger = log(__name__)


def respawn_listeners():
    """
    Re-spawns listeners from the sqlite DB

    """
    # get list of all listeners
    listeners = ListenerStore().get_all_listeners()
    # for each listener, call the spawn listener method, based on type
    # for now, only one listener type, so defaulting to HTTP

    # HEY - probably do not need a listener ID here, as it auto gets one at spawn... might create duplicate entries in the DB tho
    # also... calling the direct .spawn() will register in the DB, for sure causing dup entries...
    # best solution... have it possible to pass in a listener ID as an optional arg

    for listener in listeners:
        logger.info(
            f"Respawning listener: {listener.name}:{listener.id}@{listener.address}:{listener.port}"
        )
        http_listener = HTTPListener(
            listener_id=listener.id,
            port=listener.port,
            host=listener.address,
            name=listener.name,
        )
        http_listener.spawn()


def start_containers():
    """
    Spin up needed docker containers BEFORE loading plugins.


    """
    logger.debug("Starting redis container...")
    _start_redis_container()


def _start_redis_container():

    container_name = "redis-stack-server"
    if not container_exists(container_name):
        pull_and_run_container(
            image_name="redis/redis-stack-server",
            container_name=container_name,
            ports={"6379/tcp": 6379},
        )
        # After pulling and running, verify the container is up
        if not wait_for_container(container_name, timeout=30):
            logger.error(
                f"Container '{container_name}' failed to start within the timeout period."
            )
            # Handle the failure as needed, e.g., retry, exit, etc.
    else:
        start_container(container_name)
        # Verify the container is running
        if not wait_for_container(container_name, timeout=10):
            logger.error(f"Container '{container_name}' is not running as expected.")
            # Handle the issue as needed
