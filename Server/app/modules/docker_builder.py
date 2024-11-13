import io
import os
import re
import tarfile
from pathlib import Path
from time import sleep

import docker
from docker.errors import APIError, ImageNotFound, NotFound
from modules.log import log

logger = log(__name__)

## TODO NOW!

# Pathify paths
# cleanup + log + notes/doc


def is_valid_binary_name(name: str) -> bool:
    """
    Checks if the provided name contains only alphanumeric characters, periods and underscores.

    Args:
        name (str): The name to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9_.]+$"
    return bool(re.match(pattern, name))


class DockerBuilder:
    def __init__(
        self,
        dockerfile_path: str,
        output_dir: str,
        build_context: str,
        # build_args: dict,
        image_tag: str,
        source_code_path: str,  # source code for executabel to build
    ):
        """
        Initializes the DockerBuilder class with paths and context.

        Args:
            dockerfile_path (str): Path of the Dockerfile.
            output_dir (str): Directory to store the compiled output files.
            build_context (str): Path to the build context.
        """
        self.dockerfile_path = dockerfile_path
        self.output_dir = output_dir
        self.build_context = build_context
        self.client = docker.from_env()
        self.image_tag = image_tag
        self.container_name = None
        self.source_code_path = source_code_path

    def build_image(self):
        """
        Builds the Docker image if it doesn't already exist.

        Returns:
            image (Image): Docker image object.
        """
        try:
            # Check if the image already exists
            try:
                image = self.client.images.get(self.image_tag)
                logger.info(f"Image '{self.image_tag}' already exists. Skipping build.")
                return image
            except ImageNotFound as inf:
                logger.info(
                    f"Image '{self.image_tag}' not found. Building the image..."
                )

            # Build the image
            image, build_logs = self.client.images.build(
                path=self.build_context,
                dockerfile=self.dockerfile_path,
                tag=self.image_tag,
                rm=True,
            )

            logger.info(f"Image '{self.image_tag}' built successfully.")
            return image

        except (APIError, ValueError, Exception) as e:
            logger.error(f"Error occurred while building Docker image: {e}")
            raise e

    def create_container(self, image):
        """
        Creates a Docker container with environment variables for runtime.

        Args:
            image (Image): Docker image to create the container from.
            env_vars (dict): Optional dictionary of environment variables.

        Returns:
            container (Container): Created Docker container.
        """
        try:
            # If `image` is a string (ID or tag), retrieve the actual Image object
            if isinstance(image, str):
                image = self.client.images.get(image)

            logger.info("Creating Docker container")
            logger.debug(f"ImageID: {image.id}")

            ### Env Args

            container = self.client.containers.create(image=image.id)

            # output = container.attach(stdout=True, stream=True, logs=True)
            # for line in output:
            #    print(line)

            return container

        except (docker.errors.APIError, Exception) as e:
            logger.error(f"Error occurred while creating container: {e}")
            raise e

    def run_container(self):
        """
        Runs the container with specific environment variables and volume bindings.
        """
        try:
            logger.info("Running the Docker container with specified arguments")

            # # Define environment variables
            # env_vars = {
            #     "BINARY_NAME": "custom_binary_name",
            #     "WATCH_DIR": "/usr/src/myapp",
            #     "INTERVAL": "3",
            #     "PLATFORM": "x64"
            # }

            # Define volume bindings
            volume_bindings = {
                os.path.abspath(self.source_code_path): {
                    "bind": "/usr/src/myapp",
                    "mode": "rw",
                },
                os.path.abspath(self.output_dir): {"bind": "/output", "mode": "rw"},
            }

            # Run the container
            container = self.client.containers.run(
                image=self.image_tag,
                # environment=env_vars,
                volumes=volume_bindings,
                detach=True,  # Run in the background - DO NOT DO, need to copy runtime stuff in
                remove=True,  # Automatically remove container after it stops
            )

            logger.info("Container is running.")
            logger.debug(container.logs())
            return container

        except (docker.errors.APIError, Exception) as e:
            logger.error(f"Error occurred while running container: {e}")
            raise e

    # update when other methods are done
    def execute(self):
        """
        Main execution method to build, create container, copy files, and clean up.
        """
        try:
            # build if not exist
            image = self.build_image()

            # container = self.create_container(image)
            container = self.run_container()

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            raise e


"""
Need to:

 - Build image only if it doesn't exist. - maybe make a list of images that exist to check?
 - run image, passing in correct args
        docker run --rm 
            -v $(pwd)/agents/windows/loaders/local_shellcode_exectution:/usr/src/myapp 
            -v $(pwd)/output:/output 
            -e BINARY_NAME="custom_binary_name" 
            -e WATCH_DIR="/usr/src/myapp" 
            -e INTERVAL=3 
            -e PLATFORM="x64" dev-rust-app
            

        # copy command or whatever to copy prepared binary
        docker cp agents/windows/loaders/local_shellcode_execution/ 

"""
