import os
import tarfile

import docker
from docker.errors import APIError, NotFound
from modules.log import log

logger = log(__name__)


class DockerBuilder:
    def __init__(self, dockerfile_path: str, output_dir: str, build_context: str):
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

    def build_image(self, tag: str = "my-rust-app"):
        """
        Builds the Docker image.

        Args:
            tag (str): Tag for the Docker image.

        Returns:
            image (Image): Built Docker image.
        """
        try:
            logger.info("Building Docker image...")
            image, build_logs = self.client.images.build(
                path=self.build_context, dockerfile=self.dockerfile_path, tag=tag
            )
            return image
        except (APIError, Exception) as e:
            logger.error(f"Error occurred while building Docker image: {e}")
            raise e

    def create_container(self, image_id: str):
        """
        Creates a Docker container without starting it.

        Args:
            image_id (str): ID of the Docker image to create a container from.

        Returns:
            container (Container): Created Docker container.
        """
        try:
            logger.info("Creating Docker container...")
            return self.client.containers.create(image=image_id)
        except (APIError, NotFound, Exception) as e:
            logger.error(f"Error occurred while creating container: {e}")
            raise e

    def copy_files(self, container, src_path: str = "/output/"):
        """
        Copies any .exe files from the container to the output directory.

        Args:
            container (Container): Docker container to copy files from.
            src_path (str): Path in the container to copy files from.
        """
        try:
            # Ensure the output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info("Copying compiled .exe files from container...")

            # Get archive from the specified container directory
            tar_stream, _ = container.get_archive(src_path)
            tar_path = os.path.join(self.output_dir, "temp_output.tar")

            # Save the tar stream to a temporary tar file
            with open(tar_path, "wb") as f:
                for chunk in tar_stream:
                    f.write(chunk)

            # Extract only .exe files to the output directory
            with tarfile.open(tar_path) as tar:
                for member in tar.getmembers():
                    if member.name.endswith(".exe"):
                        # Rename the member to avoid directory structure
                        member.name = os.path.basename(member.name)
                        tar.extract(member, path=self.output_dir)
                        logger.info(f"Copied {member.name} to {self.output_dir}")

            # Clean up the tar file after extraction
            os.remove(tar_path)
            logger.info("All .exe files copied successfully.")

        except Exception as e:
            logger.error(f"Error occurred while copying files from container: {e}")
            raise e

    def clean_up_container(self, container):
        """
        Removes the specified container.

        Args:
            container (Container): Docker container to remove.
        """
        try:
            logger.info("Removing container...")
            container.remove()
        except (APIError, NotFound, Exception) as e:
            logger.error(f"Error occurred while removing container: {e}")
            raise e

    def execute(self):
        """
        Main execution method to build, create container, copy files, and clean up.
        """
        try:
            image = self.build_image()
            container = self.create_container(image.id)
            self.copy_files(container)
            self.clean_up_container(container)
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            raise e


# Usage Example:
# builder = DockerBuilder(dockerfile_path="path/to/Dockerfile", output_dir="output/dir", build_context="build/context")
# builder.execute()
