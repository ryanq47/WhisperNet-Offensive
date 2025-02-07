from modules.utils import generate_unique_id
import shutil
from modules.config import Config
import pathlib
import os
from modules.log import log

logger = log(__name__)


class HttpBuildInterface:
    def __init__(self, agent_type):

        self.build_id = generate_unique_id()

        self.agent_type = agent_type
        self.project_root = pathlib.Path(Config().root_project_path)

    def build(self):
        """
        func to do all the steps


        """

        self.copy_from_template_files()

        # on compile, thread it to let it do its thing

        return self.build_id

    def copy_to_output_folder(self):
        """
        Moves built files to prjoect_root/data/build/whatever.exe (maybe throw in the build id too)

        """

    def copy_from_template_files(self):
        """
        Copies files from template files, moves into temp build dir

        """

        # definently injectable. could copy files from system this way.
        agent_path = self.project_root / "data" / "agent_templates" / self.agent_type

        build_path = self.project_root / "data" / "build" / self.build_id

        logger.debug(f"Agent Path: {agent_path}")
        logger.debug(f"Build Path: {build_path}")

        # create the build path
        logger.debug(f"Creating build path")
        # os.makedirs(build_path, exist_ok=True) # dont need cuz the copytree makes it

        logger.debug(f"Copying template files to build path")
        ## Grab the template file based on name
        shutil.copytree(agent_path, build_path)

    def compile(self):
        """
        subprocess cmake in folder

        """

    def macro_replace(self):
        """
        Replace all the macro strings in the agents

        """
