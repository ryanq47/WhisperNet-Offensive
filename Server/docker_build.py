import docker
import os

# Initialize the Docker client
client = docker.from_env()

# Define paths
dockerfile_path = '_docker/dockerfiles/debian_windows_x64.Dockerfile'
build_context_path = '.'  # Assuming the build context is the current directory
output_dir = './agents/'

# Build the image
print("Building Docker image...")
image, build_logs = client.images.build(path=build_context_path, dockerfile=dockerfile_path, tag='my-rust-app')

# Create the container without starting it
print("Creating Docker container...")
container = client.containers.create(image.id)

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Copy files from the container
print("Copying compiled files from container...")
tar_stream, _ = container.get_archive('/output/')
with open(os.path.join(output_dir, 'output.tar'), 'wb') as f:
    for chunk in tar_stream:
        f.write(chunk)

# Extract the tar file
import tarfile
with tarfile.open(os.path.join(output_dir, 'output.tar')) as tar:
    tar.extractall(path=output_dir)

# Clean up: Remove the container
print("Removing container...")
container.remove()

# Clean up: Remove the tar file
os.remove(os.path.join(output_dir, 'output.tar'))

print("Files copied successfully to:", output_dir)
