# ----------------
## TODO:
## Need to use this to start/stop docker containers.
## Can create a watchdog later for if these go up/down.
## but need a: start & stop container
# def start_container(container_name)
# def stop_container(container_name)
# def pull_container(container_name, other dets)
# def remove_container(container_name)


# additinally, need to maek this as plugin friendly as possible. Ex, pull_contianer may be used
# by plugins a lot
# ----------------

# [ ] Replace with real logging


import socket
import time

import docker
import redis
from docker.errors import APIError, NotFound
from modules.log import log
from modules.redis_models import Container
from modules.redis_utils import redis_ping

logger = log(__name__)

client = docker.from_env()


def start_container(container_name):
    """
    Starts a container
    """
    try:
        logger.info(f"Attempting to start {container_name}")
        container = client.containers.get(container_name)
        container.start()

        if container_name == "redis-stack-server":
            if not redis_ping():
                logger.error("Redis did not become available in time.")
                return  # Exit or handle accordingly

        # dipshit... this is trying to write to redis when you JUST STARTED THE CONTAINER
        c = Container(
            name=container_name,
            # options=str(kwargs)
            image=str(container.attrs["Config"].get("Image", "")),
            volumes=str(container.attrs["Config"].get("Volumes", "")),
            hostname=str(container.attrs["Config"].get("Hostname", "")),
            ports=str(container.attrs["Config"].get("ExposedPorts", "")),
        )
        c.save()

        logger.info(f"Container '{container_name}' started.")
    except NotFound:
        logger.info(f"Container '{container_name}' not found.")
    except APIError as e:
        logger.error(f"Error starting container '{container_name}': {e}")


def stop_container(container_name):
    """
    Stops a container
    """
    try:
        container = client.containers.get(container_name)
        container.stop()
        logger.info(f"Container '{container_name}' stopped.")
    except NotFound:
        logger.info(f"Container '{container_name}' not found.")
    except APIError as e:
        logger.error(f"Error stopping container '{container_name}': {e}")


def pull_container(image_name, tag="latest"):
    """
    Pulls a container
    """
    try:
        logger.info(f"Pulling image '{image_name}:{tag}'...")
        client.images.pull(image_name, tag=tag)
        logger.info(f"Image '{image_name}:{tag}' pulled successfully.")
    except APIError as e:
        logger.error(f"Error pulling image '{image_name}:{tag}': {e}")


def pull_and_run_container(image_name, container_name, tag="latest", **kwargs):
    """
    Pulls an image and runs it with a given name
    **kwargs allows additional Docker parameters such as ports, environment variables, etc.

    Ex: pull_and_run_container(image_name="redis/redis-stack-server", container_name="redis-stack-server", ports={'6379/tcp': 6379})

    """
    try:
        if not container_exists(container_name):
            logger.info(f"Pulling image '{image_name}:{tag}'...")
            client.images.pull(image_name, tag=tag)
            logger.info(
                f"Image '{image_name}:{tag}' pulled successfully. Now running container '{container_name}'..."
            )

            container = client.containers.run(
                image=f"{image_name}:{tag}",
                name=container_name,
                detach=True,  # Run in detached mode
                **kwargs,  # Pass any additional parameters
            )

            # add details to redis
            # can expand more if needed later on.
            c = Container(
                name=container_name,
                # options=str(kwargs)
                image=str(container.attrs["Config"].get("Image", "")),
                volumes=str(container.attrs["Config"].get("Volumes", "")),
                hostname=str(container.attrs["Config"].get("Hostname", "")),
                ports=str(container.attrs["Config"].get("ExposedPorts", "")),
            )
            c.save()

            logger.info(
                f"Container '{container_name}' started successfully with image '{image_name}:{tag}'."
            )
        else:
            logger.info(f"Container '{container_name}' already exists.")
    except APIError as e:
        logger.error(e)


def wait_for_container(container_name, timeout=30, interval=2):
    """
    Waits until the specified container is running and healthy (if health checks are defined).

    :param container_name: Name of the Docker container
    :param timeout: Maximum time to wait in seconds
    :param interval: Time between checks in seconds
    :return: True if the container is running and healthy, False otherwise
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            container = client.containers.get(container_name)
            container.reload()  # Refresh container attributes

            # Check if the container is running
            if container.status != "running":
                logger.debug(f"Container '{container_name}' status: {container.status}")
                time.sleep(interval)
                continue

            # If health checks are defined, ensure the container is healthy
            health = (
                container.attrs.get("State", {})
                .get("Health", {})
                .get("Status", "unknown")
            )
            if health == "healthy":
                logger.info(f"Container '{container_name}' is healthy and running.")
                return True
            elif health == "unhealthy":
                logger.warning(f"Container '{container_name}' is unhealthy.")
                return False
            elif health == "starting":
                logger.debug(f"Container '{container_name}' is still starting...")
            else:
                # If no health check is defined, optionally verify service availability
                logger.info(
                    f"Container '{container_name}' is running and service is available."
                )
                return True
        except NotFound:
            logger.debug(f"Container '{container_name}' not found. Waiting...")
        except Exception as e:
            logger.error(f"Error while checking container '{container_name}': {e}")

        time.sleep(interval)

    logger.error(f"Timeout while waiting for container '{container_name}' to be ready.")
    return False


def remove_container(container_name, force=False):
    """
    Removes a container
    """
    try:
        container = client.containers.get(container_name)
        container.remove(force=force)
        logger.info(f"Container '{container_name}' removed.")
    except NotFound:
        logger.info(f"Container '{container_name}' not found.")
    except APIError as e:
        logger.error(f"Error removing container '{container_name}': {e}")


def container_exists(container_name):
    """
    Checks if a container exists
    Returns True if exists, False otherwise
    """
    try:
        container = client.containers.get(container_name)
        logger.info(f"Container '{container_name}' exists.")
        return True
    except NotFound:
        logger.info(f"Container '{container_name}' not found.")
        return False
    except APIError as e:
        logger.error(f"Error checking container '{container_name}': {e}")
        return False


# Example usage
if __name__ == "__main__":
    # Example calls
    pull_container("nginx")  # Pull nginx image
    start_container("my_container")  # Start container
    stop_container("my_container")  # Stop container
    remove_container("my_container")  # Remove container


## event based watchdog, this was suggested instead of implementing a loop based watchdog:
# def event_based_watchdog():
#     for event in client.events(decode=True):
#         if event['Type'] == 'container' and event['Action'] in ['start', 'stop', 'die']:
#             container_id = event['Actor']['ID']
#             container_name = event['Actor']['Attributes']['name']
#             action = event['Action']
#             print(f"Container '{container_name}' ({container_id}) has {action}.")

# if __name__ == "__main__":
#     print("Starting event-based watchdog...")
#     event_based_watchdog()
