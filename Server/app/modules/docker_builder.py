import docker
import os
from docker.errors import NotFound, APIError
from modules.log import log
import tarfile

logger = log(__name__)
client = docker.from_env()

def build(
    dockerfile_path:str,
    output_dir:str,
    build_context:str = "./data/compiled/" # pathify this

):
    '''
    dockerfile_path:str: Path of docker file. Use config file

    build_context:str: Where to "build" it from. 

    output_dir:str: output dir of the built rust file. Use config file

    '''
    try:
        logger.info("Building Docker image...")
        image, build_logs = client.images.build(path=build_context, dockerfile=dockerfile_path, tag='my-rust-app')

        # Create the container without starting it
        logger.info("Creating Docker container...")
        container = client.containers.create(image.id)

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Copy files from the container
        logger.info("Copying compiled files from container...")
        tar_stream, _ = container.get_archive('/output/')
        with open(os.path.join(output_dir, 'output.tar'), 'wb') as f:
            for chunk in tar_stream:
                f.write(chunk)

        # Extract the tar file
        with tarfile.open(os.path.join(output_dir, 'output.tar')) as tar:
            tar.extractall(path=output_dir)

        # Clean up: Remove the container
        logger.info("Removing container...")
        container.remove()

        # Clean up: Remove the tar file
        os.remove(os.path.join(output_dir, 'output.tar'))

        logger.info("Files copied successfully to:", output_dir)
    except Exception as e:
        logger.error(f"Error occured while building docker image: {e}")
        raise e