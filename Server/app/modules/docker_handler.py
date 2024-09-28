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

client = docker.from_env()

def start_container(container_name):
    '''
        Starts a container
    '''
    try:
        container = client.containers.get(container_name)
        container.start()
        print(f"Container '{container_name}' started.")
    except NotFound:
        print(f"Container '{container_name}' not found.")
    except APIError as e:
        print(f"Error starting container '{container_name}': {e}")

def stop_container(container_name):
    '''
        Stops a container
    '''
    try:
        container = client.containers.get(container_name)
        container.stop()
        print(f"Container '{container_name}' stopped.")
    except NotFound:
        print(f"Container '{container_name}' not found.")
    except APIError as e:
        print(f"Error stopping container '{container_name}': {e}")

def pull_container(image_name, tag='latest'):
    '''
        Pulls a container
    '''
    try:
        print(f"Pulling image '{image_name}:{tag}'...")
        client.images.pull(image_name, tag=tag)
        print(f"Image '{image_name}:{tag}' pulled successfully.")
    except APIError as e:
        print(f"Error pulling image '{image_name}:{tag}': {e}")

def remove_container(container_name, force=False):
    '''
        Removes a container
    '''
    try:
        container = client.containers.get(container_name)
        container.remove(force=force)
        print(f"Container '{container_name}' removed.")
    except NotFound:
        print(f"Container '{container_name}' not found.")
    except APIError as e:
        print(f"Error removing container '{container_name}': {e}")

# Example usage
if __name__ == "__main__":
    # Example calls
    pull_container("nginx")   # Pull nginx image
    start_container("my_container")   # Start container
    stop_container("my_container")    # Stop container
    remove_container("my_container")  # Remove container
