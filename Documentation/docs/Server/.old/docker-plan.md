TEMP

Docker overhaul goals

## Handle docker from python (i.e. redis server, compilation boxes, etc). 
  - Turn redis server logic into a plugin/accessible service to be controlled from the web gui?

## Think about using docker for compile targets. 

rationale: Native compiling on target OS's (except for windows). Light, and efficent, and keeps extra bs off the main box

 - Build default compile target containers at server start
    - Ubuntu
    - Cross compile box (just ubuntu with cross compile stuff?)
 - use volumes to share files
    - volumefolder/containername?
 - option to use whatever compile targets/containers you want
    - ex, arm/ubuntu, or whatever. this allows for flexibility

- Build it kinda like a lib so it's easy to access framework wise


 - Should probably include a runtest to make sure the paylaods run before returning them? step for later



 ## Safe docker sdk:

 To safely pass user input to the Python Docker SDK, use structured input handling like the environment parameter or volumes for larger data/files. Avoid including user input directly in shell commands and instead pass them as lists using command=["echo", user_input]. The SDK’s structured methods help prevent injection risks by handling input safely.

Example of Passing Commands:
```
python
Copy code
import docker

def run_container_with_args(user_input):
    client = docker.from_env()
    
    try:
        # Safely passing the user input as an argument
        container = client.containers.run(
            image="alpine",
            command=["echo", user_input],  # Input is passed as a list argument
            detach=True
        )

        # Print container logs
        print(container.logs().decode())
    except docker.errors.APIError as e:
        print(f"Error running container: {e}")

# Example usage
user_provided_value = "safe_example"
run_container_with_args(user_provided_value)
```