import io
import os
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
        # self.build_args = build_args
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

    # fine as is
    def copy_files_from_container(self, container, src_path: str = "/output/"):
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

    # use docker cp
    # switch to class vars
    def copy_files_to_container(self, container):
        logger.info("Copying files into the container")
        target_dir = "/usr/src/myapp"

        # Define source directory with Pathlib
        source_dir = Path(self.source_code_path)

        # Create a tarball in memory of the files to copy
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            for item in source_dir.rglob("*"):
                arcname = item.relative_to(source_dir)  # Preserve relative paths
                tar.add(item, arcname=str(arcname))

        tar_stream.seek(0)  # Reset stream position to the beginning

        # Upload the tarball to the container
        container.put_archive(target_dir, tar_stream.getvalue())
        logger.info("Files copied to container successfully")

    # probably fine as is
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

    # update when other methods are done
    def execute(self):
        """
        Main execution method to build, create container, copy files, and clean up.
        """
        try:
            # image = self.build_image()
            # container = self.create_container(image.id)
            # self.copy_files(container)
            # self.clean_up_container(container)

            image = self.build_image()
            # build if not exist
            container = self.create_container(image)
            # get files into it
            self.copy_files_to_container(container)
            # get files OUT of it
            self.copy_files_from_container(container)
            # prioblem - /output not being created. somethings off/script not wworking?
            # clean it up/del container
            # self.clean_up_container(container)

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
