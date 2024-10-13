# Holds class def's for binaries. May need to rename from `binary_models` if that name is no longer appropriate
from modules.binary_constructor import Loader
from modules.config import Config
from modules.docker_builder import DockerBuilder
from modules.log import log

logger = log(__name__)

# Next - fix binary_buuilder to talk to this, and test.


class Agent:
    def __init__(self, payload_name, server_address, server_port, binary_name):
        self.payload_name = payload_name
        self.server_address = server_address
        self.server_port = server_port
        self.binary_name = binary_name

        self.output_dir = str((Config().root_project_path / "data" / "compiled"))
        self.build_context = str(Config().root_project_path)

        # get values based on target/config
        # self.build_options = Config().config.server.binaries.agents.x86_windows_agent
        self.build_options = Config().config.server.binaries.agents.get(payload_name)

        logger.debug(f"Compiled output directory: {self.output_dir}")
        logger.debug(f"Docker build Context: {self.build_context}")
        logger.debug(f"Dockerfile selected to be built: {self.build_options.buildfile}")

    def build(self):
        try:
            logger.info(f"Building {self.payload_name}")
            # debug print items
            logger.debug(options for options in self.build_options.items())
            # make an async function or threaded so it can just be called.

            # build_args = {"BINARY_NAME": "URMOM.exe"}
            build_args = {
                "BINARY_NAME": self.binary_name,
                "SERVER_ADDRESS": self.server_address,
                "SERVER_PORT": self.server_port,
            }

            # build the binary
            docker_instance = DockerBuilder(
                dockerfile_path=self.build_options.buildfile,
                output_dir=self.output_dir,
                build_context=self.build_context,
                build_args=build_args,
                image_tag=self.payload_name,
            )

            docker_instance.execute()
            return True

        except ValueError as ve:
            logger.error(f"Could not build binary: {ve}")
            raise ve

        except Exception as e:
            logger.error(f"Could not build binary: {e}")
            raise e


# dep
"""class Dropper:
    def __init__(
        self,
        payload_name,
        server_address,
        server_port,
        binary_name,
        server_payload_enpoint,
    ):
        self.payload_name = payload_name
        self.server_address = server_address
        self.server_port = server_port
        self.binary_name = binary_name
        self.server_payload_enpoint = server_payload_enpoint

        self.output_dir = str((Config().root_project_path / "data" / "compiled"))
        self.build_context = str(Config().root_project_path)

        # get values based on target/config
        # self.build_options = Config().config.server.binaries.agents.x86_windows_agent
        self.build_options = Config().config.server.binaries.agents.get(payload_name)

        logger.debug(f"Compiled output directory: {self.output_dir}")
        logger.debug(f"Docker build Context: {self.build_context}")
        logger.debug(f"Dockerfile selected to be built: {self.build_options.buildfile}")

    def build(self):
        try:
            logger.info(f"Building {self.payload_name}")
            # debug print items
            logger.debug(options for options in self.build_options.items())
            # make an async function or threaded so it can just be called.

            # build_args = {"BINARY_NAME": "URMOM.exe"}
            build_args = {
                "BINARY_NAME": self.binary_name,
                "SERVER_ADDRESS": self.server_address,
                "SERVER_PORT": self.server_port,
                "SERVER_PAYLOAD_ENDPOINT": self.server_payload_enpoint,
            }

            # build the binary
            docker_instance = DockerBuilder(
                dockerfile_path=self.build_options.buildfile,
                output_dir=self.output_dir,
                build_context=self.build_context,
                build_args=build_args,
                image_tag=self.payload_name,
            )

            docker_instance.execute()
            return True

        except ValueError as ve:
            logger.error(f"Could not build binary: {ve}")
            raise ve

        except Exception as e:
            logger.error(f"Could not build binary: {e}")
            raise e
            """


class Custom:
    def __init__(self, payload_name, binary_name, payload, delivery_name):
        self.payload_name = payload_name
        self.binary_name = binary_name
        self.payload = payload
        self.delivery_name = delivery_name  # name of delivery_name method
        # get rid of absolute.
        self.output_dir = str((Config().root_project_path / "data" / "compiled"))
        self.build_context = str(Config().root_project_path)

        # get values based on target/config
        # self.build_options = Config().config.server.binaries.agents.x86_windows_agent
        self.build_options = Config().config.server.binaries.customs.get(payload_name)
        self.delivery_options = Config().config.server.binaries.delivery.get(
            delivery_name
        )

        logger.debug(f"Build Target: {self.payload_name}")
        logger.debug(f"Binary Name: {self.binary_name}")
        logger.debug(f"Payload: {self.payload}")
        logger.debug(f"Delivery method: {self.delivery_name}")
        logger.debug(f"Compiled output directory: {self.output_dir}")
        logger.debug(f"Docker build Context: {self.build_context}")
        logger.debug(f"Dockerfile selected to be built: {self.build_options.buildfile}")

    def build(self):
        try:
            logger.info(f"Building {self.payload_name}")
            # debug print items
            logger.debug(options for options in self.build_options.items())
            # make an async function or threaded so it can just be called.

            ## Construct src code
            # whatever = Loader().construct(args...)

            loader = Loader(
                loader_source_code_path=self.delivery_options.source_code,
                shellcode=self.payload,
            )

            temp_source_code_path = loader.construct()

            logger.debug("ADD IN OPTIONS FOR DOCKER CONTAINER HERE NOW")

            # build_args = {"BINARY_NAME": "URMOM.exe"}
            build_args = {
                "BINARY_NAME": self.binary_name,
                "SOURCE_CODE_PATH": str(temp_source_code_path),
                # source_code: source_code_path_from_construct
            }

            # build the binary
            docker_instance = DockerBuilder(
                dockerfile_path=self.build_options.buildfile,
                output_dir=self.output_dir,
                build_context=self.build_context,
                build_args=build_args,
                image_tag=self.payload_name,
            )

            docker_instance.execute()
            return True

        except ValueError as ve:
            logger.error(f"Could not build binary: {ve}")
            raise ve

        except Exception as e:
            logger.error(f"Could not build binary: {e}")
            raise e
