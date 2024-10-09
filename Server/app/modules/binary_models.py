
# Holds class def's for binaries. May need to rename from `binary_models` if that name is no longer appropriate
from modules.config import Config
from modules.docker_builder import DockerBuilder
from modules.log import log
logger = log(__name__)

# Next - fix binary_buuilder to talk to this, and test. 

class Agent():
    def __init__(self, build_target, server_address, server_port, executable_name):
        self.build_target = build_target 
        self.server_address = server_address
        self.server_port = server_port
        self.executable_name = executable_name

        # get rid of absolute. 
        self.output_dir = str((Config().launch_path / "data" / "compiled").absolute())
        self.build_context   = str(Config().root_project_path)

        # get values based on target/config
        #self.build_options = Config().config.server.binaries.agents.x86_windows_agent
        self.build_options = Config().config.server.binaries.agents.get(build_target)

    def build(self):
        try:
            logger.info(f"Building {self.build_target}")
            # debug print items
            logger.debug(options for options in self.build_options.items())
            # make an async function or threaded so it can just be called.

            # build the binary
            docker_instance = DockerBuilder(
                dockerfile_path = self.build_options.buildfile,
                output_dir = self.output_dir,
                build_context = self.build_context
            )

            docker_instance.execute()
            return True
        
        except Exception as e:
            logger.error(f"Could not build binary: {e}")
            raise e

    


class Dropper():
    def __init__(self, server_address, server_port, executable_name, server_payload_enpoint):
        self.server_address = server_address
        self.server_port = server_port
        self.executable_name = executable_name
        self.server_payload_enpoint = server_payload_enpoint

class Custom():
    def __init__(self, server_address, server_port, executable_name, payload):
        self.server_address = server_address
        self.server_port = server_port
        self.executable_name = executable_name
        self.payload = payload