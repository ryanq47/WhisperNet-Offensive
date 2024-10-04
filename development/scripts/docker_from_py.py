import docker

# Initialize the Docker client
client = docker.from_env()

# Pull an image
#client.images.pull('alpine')

# Run a container
#container = client.containers.run('alpine', 'echo hello world', detach=True)
#print(container.logs())

container = client.containers.get("redis-stack-server")


# List running containers
for container in client.containers.list():
    print(container.name)

config = container.attrs['Config']
host_config = container.attrs['HostConfig']

print(config)
print(host_config)

# Stop and remove the container
#ontainer.stop()
#container.remove()


