# **Python Docker Framework Documentation**

This documentation provides a breakdown of each function available in the Python Docker Framework for managing Docker containers. It covers the purpose, usage, and parameters for each function, along with example usage.

## **Overview**

This framework provides an interface to interact with Docker containers programmatically. It supports starting, stopping, pulling, removing, and monitoring Docker containers.

## Importing module

```
## All functions
from modules.docker_handler import *

## Specific Functions
from modules.docker_handler import function_name
```

## **Function Breakdown**

### 1. `start_container(container_name)`
Starts a Docker container with the specified name.

- **Parameters:**
  - `container_name` (str): The name of the container to start.

- **Example:**
  ```python
  start_container("my_container")
  ```

### 2. `stop_container(container_name)`
Stops a running Docker container by name.

- **Parameters:**
  - `container_name` (str): The name of the container to stop.

- **Example:**
  ```python
  stop_container("my_container")
  ```

### 3. `pull_container(image_name, tag='latest')`
Pulls a Docker image from the Docker registry.

- **Parameters:**
  - `image_name` (str): The name of the Docker image to pull.
  - `tag` (str, optional): The tag of the image to pull (default is 'latest').

- **Example:**
  ```python
  pull_container("nginx", tag="latest")
  ```

### 4. `pull_and_run_container(image_name, container_name, tag='latest', **kwargs)`
Pulls a Docker image and runs a container with a specified name. You can pass additional Docker parameters through `**kwargs`.

- **Parameters:**
  - `image_name` (str): The name of the Docker image to pull.
  - `container_name` (str): The name to assign to the running container.
  - `tag` (str, optional): The tag of the image to pull (default is 'latest').
  - `**kwargs`: Additional Docker parameters (e.g., ports, environment variables, etc.).

- **Example:**
  ```python
  pull_and_run_container(
      image_name="redis/redis-stack-server", 
      container_name="redis-stack-server", 
      ports={'6379/tcp': 6379}
  )
  ```

### 5. `remove_container(container_name, force=False)`
Removes a Docker container by name.

- **Parameters:**
  - `container_name` (str): The name of the container to remove.
  - `force` (bool, optional): Force removal of the container (default is `False`).

- **Example:**
  ```python
  remove_container("my_container", force=True)
  ```

### 6. `container_exists(container_name)`
Checks if a container with the specified name exists.

- **Parameters:**
  - `container_name` (str): The name of the container to check.

- **Returns:**
  - `True` if the container exists, `False` otherwise.

- **Example:**
  ```python
  if container_exists("my_container"):
      print("Container exists.")
  else:
      print("Container does not exist.")
  ```

## **Additional Watchdog Example**

This framework can be extended with an event-based watchdog to monitor container events, such as start, stop, or die actions:

### `event_based_watchdog()`
Monitors Docker events in real-time. This function listens for events like 'start', 'stop', or 'die' and logs them accordingly.

- **Example Usage:**
  ```python
  def event_based_watchdog():
      for event in client.events(decode=True):
          if event['Type'] == 'container' and event['Action'] in ['start', 'stop', 'die']:
              container_id = event['Actor']['ID']
              container_name = event['Actor']['Attributes']['name']
              action = event['Action']
              print(f"Container '{container_name}' ({container_id}) has {action}.")

  if __name__ == "__main__":
      print("Starting event-based watchdog...")
      event_based_watchdog()
  ```

## **Usage Examples**

Here’s a simple example demonstrating how to use the functions in this framework:

```python
# Example of pulling, starting, stopping, and removing a container
pull_container("nginx")           # Pulls the nginx image
start_container("nginx_container") # Starts the 'nginx_container'
stop_container("nginx_container")  # Stops the 'nginx_container'
remove_container("nginx_container")# Removes the 'nginx_container'
```

## **Notes**

- This framework is designed to be plugin-friendly. For example, the `pull_container` function can be called from other plugins/modules to ensure images are available.
- Consider replacing the print statements with more sophisticated logging mechanisms as needed.

## **Error Handling**

- The framework handles Docker API errors using try-except blocks. For example, it catches `NotFound` errors when a container does not exist and `APIError` for other Docker-related issues.



This documentation is now ready to be included in your project and provides clear guidance on how to use each function in your framework. Feel free to expand or modify as needed!