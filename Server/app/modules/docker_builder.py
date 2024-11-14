import io
import re
import tarfile
from pathlib import Path

import docker
from docker.errors import APIError, ImageNotFound, NotFound
from modules.log import log

logger = log(__name__)


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
        image_tag: str,
        source_code_path: str,
        env_args: dict,
    ):
        """
        Initializes the DockerBuilder class with paths and context.

        Args:
            dockerfile_path (str): Path of the Dockerfile.
            output_dir (str): Directory to store the compiled output files.
            build_context (str): Path to the build context.
            image_tag (str): Docker image tag.
            source_code_path (str): Path to source code for the executable to build.
        """
        # Convert paths to Path objects if they are not already
        self.dockerfile_path = Path(dockerfile_path)
        self.output_dir = Path(output_dir)
        self.build_context = Path(build_context)
        self.source_code_path = Path(source_code_path)

        self.client = docker.from_env()
        self.image_tag = image_tag
        self.container_name = None
        self.env_args = env_args

    def build_image(self):
        """
        Builds the Docker image if it doesn't already exist.

        Returns:
            image (Image): Docker image object.
        """
        try:
            try:
                image = self.client.images.get(self.image_tag)
                logger.info(f"Image '{self.image_tag}' already exists. Skipping build.")
                return image
            except ImageNotFound:
                logger.info(
                    f"Image '{self.image_tag}' not found. Building the image..."
                )

            image, build_logs = self.client.images.build(
                path=str(self.build_context),
                dockerfile=str(self.dockerfile_path),
                tag=self.image_tag,
                rm=True,
            )
            logger.info(f"Image '{self.image_tag}' built successfully.")
            return image

        except (APIError, ValueError, Exception) as e:
            logger.error(f"Error occurred while building Docker image: {e}")
            raise e

    # def create_container(self, image):
    #     """
    #     Creates a Docker container with environment variables for runtime.

    #     Args:
    #         image (Image): Docker image to create the container from.

    #     Returns:
    #         container (Container): Created Docker container.
    #     """
    #     try:
    #         if isinstance(image, str):
    #             image = self.client.images.get(image)

    #         logger.info("Creating Docker container")
    #         logger.debug(f"ImageID: {image.id}")

    #         container = self.client.containers.create(image=image.id)
    #         return container

    #     except (docker.errors.APIError, Exception) as e:
    #         logger.error(f"Error occurred while creating container: {e}")
    #         raise e

    def run_container(self):
        """
        Runs the container with specific environment variables and volume bindings.
        """
        try:
            logger.info("Running the Docker container with specified arguments")

            # Define volume bindings
            volume_bindings = {
                str(self.source_code_path.resolve()): {
                    "bind": "/usr/src/myapp",
                    "mode": "rw",
                },
                str(self.output_dir.resolve()): {"bind": "/output", "mode": "rw"},
            }

            logger.debug(f"Env Args: {self.env_args}")

            container = self.client.containers.run(
                image=self.image_tag,
                volumes=volume_bindings,
                detach=False,  # Run in the foreground to capture logs
                remove=True,  # Automatically remove container after it stops
                environment=self.env_args,  # pass in env args
            )

            logger.info("Container is running.")
            # logger.debug(container.logs())
            return container

        except (docker.errors.APIError, Exception) as e:
            logger.error(f"Error occurred while running container: {e}")
            raise e

    def execute(self):
        """
        Main execution method to build, create container, copy files, and clean up.
        """
        try:
            image = self.build_image()
            container = self.run_container()
            logger.debug("Container ran successfully")

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            raise e
