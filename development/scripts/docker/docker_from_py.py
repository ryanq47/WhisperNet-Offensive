import docker

# Initialize the Docker client
client = docker.from_env()

# Pull an image
client.images.pull('alpine')

# Run a container
container = client.containers.run('alpine', 'echo hello world', detach=True)
print(container.logs())

# List running containers
for container in client.containers.list():
    print(container.name)

# Stop and remove the container
container.stop()
container.remove()


