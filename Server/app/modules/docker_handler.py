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



import docker
from docker.errors import NotFound, APIError
from modules.log import log
from modules.redis_models import Container

logger = log(__name__)

client = docker.from_env()

def start_container(container_name):
    '''
        Starts a container
    '''
    try:
        container = client.containers.get(container_name)
        container.start()

        c = Container(
                name=container_name,
                #options=str(kwargs)
                image=str(container.attrs['Config'].get("Image","")),
                volumes=str(container.attrs['Config'].get("Volumes","")),
                hostname=str(container.attrs['Config'].get("Hostname","")),
                ports=str(container.attrs['Config'].get("ExposedPorts","")),
            )
        c.save()

        logger.info(f"Container '{container_name}' started.")
    except NotFound:
        logger.info(f"Container '{container_name}' not found.")
    except APIError as e:
        logger.error(f"Error starting container '{container_name}': {e}")

def stop_container(container_name):
    '''
        Stops a container
    '''
    try:
        container = client.containers.get(container_name)
        container.stop()
        logger.info(f"Container '{container_name}' stopped.")
    except NotFound:
        logger.info(f"Container '{container_name}' not found.")
    except APIError as e:
        logger.error(f"Error stopping container '{container_name}': {e}")

def pull_container(image_name, tag='latest'):
    '''
        Pulls a container
    '''
    try:
        logger.info(f"Pulling image '{image_name}:{tag}'...")
        client.images.pull(image_name, tag=tag)
        logger.info(f"Image '{image_name}:{tag}' pulled successfully.")
    except APIError as e:
        logger.error(f"Error pulling image '{image_name}:{tag}': {e}")

def pull_and_run_container(image_name, container_name, tag='latest', **kwargs):
    '''
        Pulls an image and runs it with a given name
        **kwargs allows additional Docker parameters such as ports, environment variables, etc.

        Ex: pull_and_run_container(image_name="redis/redis-stack-server", container_name="redis-stack-server", ports={'6379/tcp': 6379})

    '''
    try:
        if not container_exists(container_name):
            logger.info(f"Pulling image '{image_name}:{tag}'...")
            client.images.pull(image_name, tag=tag)
            logger.info(f"Image '{image_name}:{tag}' pulled successfully. Now running container '{container_name}'...")

            container = client.containers.run(
                image=f"{image_name}:{tag}",
                name=container_name,
                detach=True,  # Run in detached mode
                **kwargs      # Pass any additional parameters
            )
            
            # add details to redis
            # can expand more if needed later on. 
            c = Container(
                name=container_name,
                #options=str(kwargs)
                image=str(container.attrs['Config'].get("Image","")),
                volumes=str(container.attrs['Config'].get("Volumes","")),
                hostname=str(container.attrs['Config'].get("Hostname","")),
                ports=str(container.attrs['Config'].get("ExposedPorts","")),
            )
            c.save()

            logger.info(f"Container '{container_name}' started successfully with image '{image_name}:{tag}'.")
        else:
            logger.info(f"Container '{container_name}' already exists.")
    except APIError as e:
        logger.error(e)

def remove_container(container_name, force=False):
    '''
        Removes a container
    '''
    try:
        container = client.containers.get(container_name)
        container.remove(force=force)
        logger.info(f"Container '{container_name}' removed.")
    except NotFound:
        logger.info(f"Container '{container_name}' not found.")
    except APIError as e:
        logger.error(f"Error removing container '{container_name}': {e}")

def container_exists(container_name):
    '''
        Checks if a container exists
        Returns True if exists, False otherwise
    '''
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
    pull_container("nginx")   # Pull nginx image
    start_container("my_container")   # Start container
    stop_container("my_container")    # Stop container
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
